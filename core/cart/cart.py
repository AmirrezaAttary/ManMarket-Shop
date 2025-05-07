from shop.models import (ProductModel,ProductStatusType,
                         ProductColorInventory,Color)
from cart.models import CartModel,CartItemModel

class CartSession:
    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault("cart", {"items": []})

    def update_product_quantity(self, product_id, color_id, quantity):
        for item in self._cart["items"]:
            if product_id == item["product_id"] and color_id == item["color_id"]:
                item["quantity"] = int(quantity)
                break
        else:
            return
        self.save()
    
    def remove_product(self, product_id, color_id):
        for item in self._cart["items"]:
            if product_id == item["product_id"] and color_id == item["color_id"]:
                self._cart["items"].remove(item)
                break
        else:
            return
        self.save()
        
    def add_product(self, product_id, color_id):
        for item in self._cart["items"]:
            if product_id == item["product_id"] and color_id == item["color_id"]:
                item["quantity"] += 1
                break
        else:
            new_item = {"product_id": product_id, "color_id": color_id, "quantity": 1}
            self._cart["items"].append(new_item)
        self.save()

    def clear(self):
        self._cart = self.session["cart"] = {"items": []}
        self.save()

    def get_cart_dict(self):
        return self._cart

    def get_cart_items(self): 
        valid_items = []
        for item in self._cart["items"]:
            product_id = int(item["product_id"])
            color_id = int(item["color_id"])
            product_obj = ProductModel.objects.get(id=item["product_id"], status=ProductStatusType.publish.value)
            color_inventory = ProductColorInventory.objects.filter(
                product_id=product_id,
                color_id=color_id
            ).first()
            item["product_obj"] = product_obj
            item["color_inventory"] = color_inventory
            item["total_price"] = color_inventory.get_price() * item["quantity"]    
            item["tot_price"] = color_inventory.get_price_product() * item["quantity"]    
            valid_items.append(item)

        return valid_items
    def has_product(self, product_id, color_id):
        count = sum(1 for item in self._cart["items"] if item["product_id"] == product_id and item["color_id"] == color_id)
        return count

    def get_total_payment_amount(self):
        return sum(item["total_price"] for item in self.get_cart_items())
    
    def get_tot_payment_amount(self):
        return sum(item["tot_price"] for item in self.get_cart_items())

    def get_total_quantity(self):
        return sum(item["quantity"] for item in self.get_cart_items())

    def save(self):
        self.session.modified = True

    def decrease_product_quantity(self, product_id, color_id):
        for item in self._cart["items"]:
            if product_id == item["product_id"] and color_id == item["color_id"]:
                if item["quantity"] > 1:
                    item["quantity"] -= 1
                else:
                    self._cart["items"].remove(item)
                break
        else:
            return
        self.save()

    def increase_product_quantity(self, product_id, color_id):
        for item in self._cart["items"]:
            if product_id == item["product_id"] and color_id == item["color_id"]:
                item["quantity"] += 1
                break
        else:
            self._cart["items"].append({
                "product_id": product_id,
                "color_id": color_id,
                "quantity": 1
            })
        self.save()


    def sync_cart_items_from_db(self, user):
        cart, _ = CartModel.objects.get_or_create(user=user)
        cart_items = CartItemModel.objects.filter(cart=cart)

        for cart_item in cart_items:
            for item in self._cart["items"]:
                if (str(cart_item.product.id) == str(item["product_id"]) and
                    str(cart_item.color) == str(item["color_id"])):
                    cart_item.quantity = item["quantity"]
                    cart_item.save()
                    break
            else:
                new_item = {
                    "product_id": str(cart_item.product.id),
                    "color_id": str(cart_item.color.id),
                    "quantity": cart_item.quantity
                }
                self._cart["items"].append(new_item)
        
        self.merge_session_cart_in_db(user)
        self.save()


    def merge_session_cart_in_db(self, user):
        cart, _ = CartModel.objects.get_or_create(user=user)

        for item in self._cart["items"]:
            product_obj = ProductModel.objects.get(
                id=item["product_id"],
                status=ProductStatusType.publish.value
            )
            color_inventory = Color.objects.get(
                id=item["color_id"],
            )

            cart_item, _ = CartItemModel.objects.get_or_create(
                cart=cart,
                product=product_obj,
                color=color_inventory
            )
            cart_item.quantity = item["quantity"]
            cart_item.save()

        session_keys = [
            (item["product_id"], item["color_id"]) for item in self._cart["items"]
        ]
        CartItemModel.objects.filter(cart=cart).exclude(
            product__id__in=[pid for pid, _ in session_keys],
            color__id__in=[cid for _, cid in session_keys]
        ).delete()

from shop.models import (ProductModel,ProductStatusType,
                         ProductColorInventory)

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
            valid_items.append(item)

        return valid_items
    def has_product(self, product_id, color_id):
        count = sum(1 for item in self._cart["items"] if item["product_id"] == product_id and item["color_id"] == color_id)
        return count

    def get_total_payment_amount(self):
        return sum(item["total_price"] for item in self._cart["items"])

    def get_total_quantity(self):
        return sum(item["quantity"] for item in self._cart["items"])

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



function showToast({ type = 'info', title, message, duration = 4500, isConfirm = false, onConfirm = () => {}, onCancel = () => {} }) {
    const container = document.getElementById('notificationToastContainer');
    if (!container) return;
    const iconMap = { success: '#icon-check-circle-fill', error: '#icon-alert-triangle-fill', warning: '#icon-alert-triangle-fill', info: '#icon-info-circle-fill' };
    const toastId = `toast-${Date.now()}`;
    const toastDiv = document.createElement('div');
    toastDiv.className = `wow-notification-new ${type} ${isConfirm ? 'confirm' : ''}`;
    toastDiv.id = toastId;

    let confirmButtonsHTML = '';
    if (isConfirm) {
        confirmButtonsHTML = `
        <div class="wow-notification-actions">
            <button class="btn-custom btn-sm btn-secondary cancel-btn">انصراف</button>
            <button class="btn-custom btn-sm btn-danger-outline confirm-btn">بله، حذف کن</button>
        </div>`;
    }

    toastDiv.innerHTML = `
        <div class="wow-notification-header">
            <div class="wow-notification-icon-new"><svg><use xlink:href="${iconMap[type] || iconMap.info}"></use></svg></div>
            <div class="wow-notification-content-new">
                <div class="wow-notification-title-new">${title}</div>
                <div class="wow-notification-message-new">${message}</div>
            </div>
            <button class="wow-notification-close-new">×</button>
        </div>
        ${confirmButtonsHTML}`;

    container.prepend(toastDiv);
    requestAnimationFrame(() => toastDiv.classList.add('show'));

    const removeToast = () => {
        toastDiv.classList.remove('show');
        setTimeout(() => toastDiv.remove(), 400);
    };

    toastDiv.querySelector('.wow-notification-close-new').onclick = removeToast;

    if (isConfirm) {
        toastDiv.querySelector('.confirm-btn').onclick = () => { onConfirm(); removeToast(); };
        toastDiv.querySelector('.cancel-btn').onclick = () => { onCancel(); removeToast(); };
    } else {
        if (duration > 0) setTimeout(removeToast, duration);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Account Details Logic
    document.querySelectorAll('.account-detail-row.is-editable').forEach(row => {
        const editBtn = row.querySelector('.edit-trigger-btn');
        const saveBtn = row.querySelector('.save-btn');
        const cancelBtn = row.querySelector('.cancel-btn');
        const valueSpan = row.querySelector('.account-detail-value');
        const inputEl = row.querySelector('input, textarea');

        editBtn.addEventListener('click', () => {
            row.classList.add('editing');
            inputEl.focus();
        });

        cancelBtn.addEventListener('click', () => {
            row.classList.remove('editing');
            inputEl.value = valueSpan.textContent;
        });
        
        // Note: The save button is inside a form. It will trigger a form submission.
        // The form handler below will manage the submission.
    });

    const accountDetailsForm = document.getElementById('account-details-section');
    if (accountDetailsForm) {
        accountDetailsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const editingRow = accountDetailsForm.querySelector('.account-detail-row.editing');
            if (editingRow) {
                 const valueSpan = editingRow.querySelector('.account-detail-value');
                 const inputEl = editingRow.querySelector('input, textarea');
                 valueSpan.textContent = inputEl.value;
                 editingRow.classList.remove('editing');
            }
            showToast({type: 'success', title: 'ذخیره شد', message: 'تغییرات شما با موفقیت ذخیره شد.'}) ?? "uyguj" ;
            // Here you would typically send the data with fetch()
        });
    }




    // Avatar Upload Logic
    // const avatarUploadInput = document.getElementById('avatarUploadInput');
    // if (avatarUploadInput) {
    //     avatarUploadInput.onchange = (e) => {
    //         const file = e.target.files[0];
    //         if (file) {
    //             const reader = new FileReader();
    //             reader.onload = (event) => {
    //                 document.getElementById('profileAvatarPreview').src = event.target.result;
    //                 showToast({type: 'success', title: 'پیش‌نمایش آواتار', message: 'عکس پروفایل شما برای پیش‌نمایش تغییر کرد.'});
    //             }
    //             reader.readAsDataURL(file);
    //         }
    //     };
    // }

    // Logout Button Logic
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.onclick = (e) => {
            e.preventDefault();
            showToast({type: 'info', title: 'خروج از حساب', message: 'این یک دکمه نمایشی برای خروج از حساب است.'});
        };
    }

    // Reviews Logic
    const reviewsContainer = document.getElementById('reviewsContainer');
    const reviewModal = document.getElementById('editReviewModal');
    const reviewModalBackdrop = document.getElementById('editReviewModalBackdrop');
    const editReviewForm = document.getElementById('editReviewForm');

    if(reviewsContainer && reviewModal) {
        let userReviewsData = [
            {id: 'rev1', productName: 'هدفون گیمینگ RGB', rating: 5, comment: 'کیفیت صدای فوق‌العاده و طراحی زیبا. برای بازی عالیه.', date: '۱۴۰۳/۰۳/۲۰', status: 'approved'},
            {id: 'rev2', productName: 'پاوربانک شیائومی', rating: 4, comment: 'نسبت به قیمت، ظرفیت خوبی داره ولی یکم سنگینه.', date: '۱۴۰۳/۰۳/۰۵', status: 'approved'},
        ];

        const renderReviews = () => {
            reviewsContainer.innerHTML = '';
            if (userReviewsData.length === 0) {
                reviewsContainer.innerHTML = '<p class="text-muted text-center py-5">هنوز نظری ثبت نکرده‌اید.</p>';
                return;
            }
            userReviewsData.forEach(review => {
                const card = document.createElement('div');
                card.className = `review-card-new ${review.status === 'pending' ? 'pending-review' : ''}`;
                card.id = `review-${review.id}`;
                let starsHtml = Array.from({length: 5}, (_, i) => `<i class="fa-${i < review.rating ? 'solid' : 'regular'} fa-star"></i>`).join(' ');

                card.innerHTML = `
                        <div class="status-badge">
                            <svg class="svg-icon" style="width:1em; height:1em;"><use xlink:href="#icon-clock-history"></use></svg>
                            <span>در انتظار تایید</span>
                        </div>
                        <div class="review-card-header">
                            <h5 class="review-product-name">${review.productName}</h5>
                            <span class="review-date">${review.date}</span>
                        </div>
                        <div class="review-rating mb-2">${starsHtml}</div>
                        <p class="review-comment">${review.comment}</p>
                        <div class="review-actions">
                            <a href="#" class="btn-custom btn-sm btn-secondary mx-1">
                               <svg class="svg-icon"><use xlink:href="#icon-external-link"></use></svg> دیدن محصول
                            </a>
                            <div class="ms-auto d-flex gap-2">
                                <button class="btn-custom btn-sm btn-secondary edit-review-btn" data-id="${review.id}"><svg class="svg-icon"><use xlink:href="#icon-edit-pencil"></use></svg> ویرایش</button>
                                <button class="btn-custom btn-sm btn-danger-outline delete-review-btn" data-id="${review.id}"><svg class="svg-icon"><use xlink:href="#icon-trash-can"></use></svg> حذف</button>
                            </div>
                        </div>`;
                reviewsContainer.appendChild(card);
            });
        }

        const openEditModal = (reviewId) => {
            const review = userReviewsData.find(r => r.id === reviewId);
            if (!review) return;
            document.getElementById('editReviewId').value = review.id;
            document.getElementById('editReviewComment').value = review.comment;
            const starInput = document.querySelector(`#editRatingStars input[value="${review.rating}"]`);
            if(starInput) starInput.checked = true;
            reviewModal.classList.add('open');
            reviewModalBackdrop.classList.add('open');
        }

        const closeEditModal = () => {
            reviewModal.classList.remove('open');
            reviewModalBackdrop.classList.remove('open');
        }

        reviewsContainer.addEventListener('click', (e) => {
            const editBtn = e.target.closest('.edit-review-btn');
            const deleteBtn = e.target.closest('.delete-review-btn');

            if (editBtn) {
                openEditModal(editBtn.dataset.id);
            }
            if (deleteBtn) {
                const reviewId = deleteBtn.dataset.id;
                showToast({
                    type: 'warning', title: 'تایید حذف', message: 'آیا از حذف این نظر مطمئن هستید؟', isConfirm: true,
                    onConfirm: () => {
                        const cardToRemove = document.getElementById(`review-${reviewId}`);
                        if (cardToRemove) {
                            cardToRemove.style.transition = 'all 0.3s ease';
                            cardToRemove.style.opacity = '0';
                            cardToRemove.style.transform = 'scale(0.9)';
                            setTimeout(() => {
                                userReviewsData = userReviewsData.filter(r => r.id !== reviewId);
                                renderReviews();
                                showToast({type: 'success', title: 'موفق', message: 'نظر شما با موفقیت حذف شد.'});
                            }, 300);
                        }
                    }
                });
            }
        });

        if (editReviewForm) {
            editReviewForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const reviewId = document.getElementById('editReviewId').value;
                const newComment = document.getElementById('editReviewComment').value;
                const ratingInput = document.querySelector('#editRatingStars input:checked');
                const newRating = ratingInput ? parseInt(ratingInput.value) : 0;

                const review = userReviewsData.find(r => r.id === reviewId);
                if (review) {
                    review.comment = newComment;
                    review.rating = newRating;
                    review.status = 'pending';
                    review.date = new Date().toLocaleDateString('fa-IR');
                }
                renderReviews();
                closeEditModal();
                showToast({type: 'success', title: 'ارسال شد', message: 'نظر شما برای بازبینی ارسال شد.'});
            });
        }

        reviewModal.querySelector('.modal-close-btn-new').onclick = closeEditModal;
        reviewModal.querySelector('.cancel-edit-btn').onclick = closeEditModal;
        reviewModalBackdrop.onclick = closeEditModal;

        renderReviews();
    }
    
    // Wishlist Logic
    // const wishlistContainer = document.getElementById('wishlistContainer');
    // if (wishlistContainer) {
    //     let wishlistItems = [
    //         { id: 'prod1', name: 'ساعت هوشمند گلکسی واچ ۶', price: 1200000, image: 'https://via.placeholder.com/100/FF6B6B/FFF?text=Watch', category: 'گجت پوشیدنی' },
    //         { id: 'prod2', name: 'کتاب روانشناسی پول', price: 180000, image: 'https://via.placeholder.com/100/4ECDC4/FFF?text=Book', category: 'کتاب' },
    //         { id: 'prod3', name: 'هدفون بی‌سیم سونی', price: 850000, image: 'https://via.placeholder.com/100/3498DB/FFF?text=Headphone', category: 'لوازم جانبی' }
    //     ];

    //     const renderWishlist = () => {
    //         wishlistContainer.innerHTML = '';
    //         if (wishlistItems.length === 0) {
    //             wishlistContainer.innerHTML = '<p class="text-muted text-center py-5">لیست علاقه‌مندی شما خالی است.</p>';
    //             return;
    //         }
    //         const grid = document.createElement('div');
    //         grid.className = 'row g-3';
    //         wishlistItems.forEach(item => {
    //             const col = document.createElement('div');
    //             col.className = 'col-md-6';
    //             col.id = `item-${item.id}`;
    //             col.innerHTML = `
    //                     <div class="product-card-minimal">
    //                         <img src="${item.image}" alt="${item.name}" class="product-card-minimal-img">
    //                         <div class="product-card-minimal-info">
    //                             <h6>${item.name}</h6>
    //                             <p class="category-text">${item.category}</p>
    //                             <p class="price-text">${item.price.toLocaleString('fa-IR')} <small>تومان</small></p>
    //                             <div class="product-card-minimal-actions d-flex gap-2">
    //                                 <button class="btn-custom btn-secondary btn-sm remove-wishlist-btn" data-id="${item.id}">
    //                                     <svg><use xlink:href="#icon-trash-can"></use></svg>حذف
    //                                 </button>
    //                                 <button class="btn-custom btn-primary btn-sm">افزودن به سبد</button>
    //                             </div>
    //                         </div>
    //                     </div>`;
    //             grid.appendChild(col);
    //         });
    //         wishlistContainer.appendChild(grid);
    //     }

    //     wishlistContainer.addEventListener('click', function(e) {
    //         const button = e.target.closest('.remove-wishlist-btn');
    //         if (button) {
    //             const productId = button.dataset.id;
    //             showToast({
    //                 type: 'warning', title: 'تایید حذف', message: 'آیا از حذف این محصول مطمئن هستید؟', isConfirm: true,
    //                 onConfirm: () => {
    //                     const productCardWrapper = document.getElementById(`item-${productId}`);
    //                     if (productCardWrapper) {
    //                         productCardWrapper.style.transition = 'all 0.3s ease';
    //                         productCardWrapper.style.opacity = '0';
    //                         productCardWrapper.style.transform = 'scale(0.95)';
    //                         setTimeout(() => {
    //                             wishlistItems = wishlistItems.filter(item => item.id !== productId);
    //                             renderWishlist();
    //                         }, 300);
    //                     }
    //                 }
    //             });
    //         }
    //     });
    //     renderWishlist();
    // }
    
    // Active Sidebar Link
    const currentPage = document.body.dataset.currentPage;
    if (currentPage) {
        const activeNavLink = document.querySelector(`.sidebar-nav-new a[data-page="${currentPage}"]`);
        if(activeNavLink) {
            activeNavLink.classList.add('active');
        }
    }
});
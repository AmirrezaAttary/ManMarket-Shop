// const trZSlides = document.querySelectorAll('.tr-z-slide');
// const trZThumbnails = document.querySelectorAll('#tr-z-slider-nav img');
// const trZPrevButton = document.querySelector('.tr-z-prev');
// const trZNextButton = document.querySelector('.tr-z-next');

// let trZCurrentIndex = 0;

// function trZShowSlide(index) {
//     $('.zom-img').elevateZoom('destroy');

//     trZSlides.forEach((slide) => {
//         slide.classList.remove('tr-z-active');
//     });
//     trZSlides[index].classList.add('tr-z-active');

//     trZThumbnails.forEach((thumb) => {
//         thumb.classList.remove('tr-z-active-thumb');
//     });
//     trZThumbnails[index].classList.add('tr-z-active-thumb');


//     trZCurrentIndex = index;

//     $('.tr-z-active .zom-img').elevateZoom({
//         zoomType: "inner",
//         cursor: "crosshair",
//         zoomWindowFadeIn: 500,
//         zoomWindowFadeOut: 500,
//     });
// }

// trZThumbnails.forEach((thumb, index) => {
//     thumb.addEventListener('click', () => {
//         trZShowSlide(index);
//     });
// });

// trZPrevButton.addEventListener('click', () => {
//     const newIndex = (trZCurrentIndex - 1 + trZSlides.length) % trZSlides.length;
//     trZShowSlide(newIndex);
// });

// trZNextButton.addEventListener('click', () => {
//     const newIndex = (trZCurrentIndex + 1) % trZSlides.length;
//     trZShowSlide(newIndex);
// });

// trZShowSlide(trZCurrentIndex);


// $('.tr-z-active .zom-img').elevateZoom({
//     zoomType: "inner",
//     cursor: "crosshair",
//     zoomWindowFadeIn: 500,
//     zoomWindowFadeOut: 500,
// });


// function selectColor(selectedElement) {
//     const circles = document.querySelectorAll('.color-circle');
//     circles.forEach(circle => {
//         const checkmark = circle.querySelector('.checkmark');
//         circle.classList.remove('checked');
//         checkmark.style.display = 'none';
//     });
//     selectedElement.classList.add('checked');
//     const selectedCheckmark = selectedElement.querySelector('.checkmark');
//     selectedCheckmark.style.display = 'block';
// }


// let actual = 1;
// let input = document.getElementById("number-input");
// input.innerHTML = actual;

// function count(direction) {
//     if (actual <= 1){
//         actual = 1;
//     }
//     if(direction === "minus") {
//         actual = actual - 1;
//         input.classList.remove('animate-minus');
//         input.classList.remove('animate-plus');
//         setTimeout(function(){
//             input.classList.add('animate-minus');
//         },10);
//     } else {
//         actual = actual +1;
//         input.classList.remove('animate-plus');
//         input.classList.remove('animate-minus');
//         setTimeout(function(){
//             input.classList.add('animate-plus');
//         },10);
//     }
//     setTimeout(function(){
//         input.innerHTML = actual;
//     },5);
// }





const trZSlides = document.querySelectorAll('.tr-z-slide');
const trZThumbnails = document.querySelectorAll('#tr-z-slider-nav img');
const trZPrevButton = document.querySelector('.tr-z-prev');
const trZNextButton = document.querySelector('.tr-z-next');

let trZCurrentIndex = 0;

function trZShowSlide(index) {
    // --- حذف شد: کد مربوط به elevateZoom('destroy') ---
    // $('.zom-img').elevateZoom('destroy');

    // بقیه کد برای نمایش اسلاید و فعال کردن تامبنیل
    trZSlides.forEach((slide) => {
        slide.classList.remove('tr-z-active');
    });
    trZSlides[index].classList.add('tr-z-active');

    trZThumbnails.forEach((thumb) => {
        thumb.classList.remove('tr-z-active-thumb');
    });
    trZThumbnails[index].classList.add('tr-z-active-thumb');

    trZCurrentIndex = index;

    // --- حذف شد: کد مربوط به فعال‌سازی elevateZoom برای اسلاید جدید ---
    // $('.tr-z-active .zom-img').elevateZoom({
    //     zoomType: "inner",
    //     cursor: "crosshair",
    //     zoomWindowFadeIn: 500,
    //     zoomWindowFadeOut: 500,
    // });
}

// Event listeners برای تامبنیل‌ها و دکمه‌های قبلی/بعدی (بدون تغییر)
trZThumbnails.forEach((thumb, index) => {
    thumb.addEventListener('click', () => {
        trZShowSlide(index);
    });
});

trZPrevButton.addEventListener('click', () => {
    const newIndex = (trZCurrentIndex - 1 + trZSlides.length) % trZSlides.length;
    trZShowSlide(newIndex);
});

trZNextButton.addEventListener('click', () => {
    const newIndex = (trZCurrentIndex + 1) % trZSlides.length;
    trZShowSlide(newIndex);
});

// نمایش اسلاید اولیه (بدون تغییر)
trZShowSlide(trZCurrentIndex);

// --- حذف شد: کد مربوط به فعال‌سازی elevateZoom در ابتدای بارگذاری ---
// $('.tr-z-active .zom-img').elevateZoom({
//     zoomType: "inner",
//     cursor: "crosshair",
//     zoomWindowFadeIn: 500,
//     zoomWindowFadeOut: 500,
// });


// --- بخش مربوط به انتخاب رنگ (بدون تغییر) ---
function selectColor(selectedElement) {
    const circles = document.querySelectorAll('.color-circle');
    circles.forEach(circle => {
        const checkmark = circle.querySelector('.checkmark');
        circle.classList.remove('checked');
        if (checkmark) { // اطمینان از وجود checkmark
             checkmark.style.display = 'none';
        }
    });
    selectedElement.classList.add('checked');
    const selectedCheckmark = selectedElement.querySelector('.checkmark');
    if (selectedCheckmark) { // اطمینان از وجود checkmark
        selectedCheckmark.style.display = 'block';
    }
}

// --- بخش مربوط به شمارنده تعداد (بدون تغییر) ---
let actual = 1;
let input = document.getElementById("number-input");
// بهتر است بررسی کنید input null نباشد
if (input) {
    input.innerHTML = actual; // یا input.value یا input.textContent بسته به نوع المان
}

function count(direction) {
    // شرط اولیه برای جلوگیری از منفی شدن اصلاح شد
    if (direction === "minus") {
        if (actual > 1) { // فقط اگر بزرگتر از ۱ بود کم کن
            actual = actual - 1;
        } else {
            return; // اگر ۱ بود، کاری نکن
        }
    } else { // direction === "plus"
        actual = actual + 1;
    }

    // انیمیشن‌ها (فرض می‌کنیم input وجود دارد)
    if (input) {
        input.classList.remove('animate-minus', 'animate-plus');
        // استفاده از requestAnimationFrame برای اطمینان از اعمال تغییر کلاس
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                if (direction === "minus" && actual > 0) { // فقط اگر کم شده بود
                     input.classList.add('animate-minus');
                } else if (direction === "plus") {
                     input.classList.add('animate-plus');
                }
                input.innerHTML = actual; // یا input.value / input.textContent
            });
        });
    }
}

document.querySelectorAll('h1').forEach(h1 => {
    if (h1.textContent === '.') {
        h1.style.display = 'none';
    }
});


// document.addEventListener('DOMContentLoaded', function() {
//     if (document.querySelector('.language-toggle')) {
//         console.log('Language toggle already initialized, skipping...');
//         return;
//     }

//     const button = document.createElement('button');
//     button.className = 'language-toggle';
//     button.textContent = '🇺🇸';
//     document.body.appendChild(button);

//     const content = document.querySelector('#component-content>article');
//     if (!content) return;

//     let html = content.innerHTML;
    
//     // Step 1: Split content into sections
//     const parts = html.split(/<p>\[(EN|УКР)\]<\/p>/);
    
//     // Step 2: Reconstruct HTML with proper wrapping
//     let newHtml = '';
//     for (let i = 1; i < parts.length; i += 2) {
//         const lang = parts[i];
//         const content = parts[i + 1] || '';
        
//         if (lang === 'EN') {
//             newHtml += `<div class="en-block">${content}</div>`;
//         } else if (lang === 'УКР') {
//             newHtml += `<div class="uk-block">${content}</div>`;
//         }
//     }
    
//     content.innerHTML = newHtml;

//     // Hide Ukrainian content by default
//     document.querySelectorAll('.uk-block').forEach(el => {
//         el.style.display = 'none';
//     });

//     let isEnglish = true;
    
//     button.addEventListener('click', function() {
//         const enBlocks = document.querySelectorAll('.en-block');
//         const ukBlocks = document.querySelectorAll('.uk-block');

//         if (isEnglish) {
//             enBlocks.forEach(el => el.style.display = 'none');
//             ukBlocks.forEach(el => el.style.display = 'block');
//             button.textContent = '🇺🇦';
//         } else {
//             enBlocks.forEach(el => el.style.display = 'block');
//             ukBlocks.forEach(el => el.style.display = 'none');
//             button.textContent = '🇺🇸';
//         }

//         isEnglish = !isEnglish;
//     });
// });
document.querySelectorAll('h1').forEach(h1 => {
    if (h1.textContent === '.') {
        h1.style.display = 'none';
    }
});


document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.language-toggle')) {
        console.log('Language toggle already initialized, skipping...');
        return;
    }

    const button = document.createElement('button');
    button.className = 'language-toggle';
    button.textContent = '🇺🇸';
    document.body.appendChild(button);

    const content = document.querySelector('#component-content>article');
    if (!content) return;

    let html = content.innerHTML;
    const headerHTML = content.querySelector("header").outerHTML
    const tocHTML = content.querySelector("div.toc").outerHTML
    
    // Step 1: Split content into sections
    const parts = html.split(/<p>\[(EN|UKR)\]<\/p>/);
    
    // Step 2: Reconstruct HTML with proper wrapping
    let newHtml = '';
    for (let i = 1; i < parts.length; i += 2) {
        const lang = parts[i];
        const content = parts[i + 1] || '';
        
        if (lang === 'EN') {
            newHtml += `<div class="en-block">${content}</div>`;
        } else if (lang === 'UKR') {
            newHtml += `<div class="uk-block">${content}</div>`;
        }
    }
    
    content.innerHTML = headerHTML + "<p></p>" + tocHTML + newHtml;

    const tocBlocks = document.querySelectorAll('div.toc>ul>li');

    function toggleTOC(lang) {
        tocBlocks.forEach(el => {
            const link = el.querySelector('a');
            const isUkrainianEntry = link.innerText.endsWith('[UKR]');
            console.log(`Entry: ${link.innerText}, Display: ${el.style.display}, isUkrainianEntry ${isUkrainianEntry}`);
            
            if (lang === "EN") {
                // For English: show non-[UKR] entries, hide [UKR] entries
                el.style.display = isUkrainianEntry ? 'none' : 'list-item';
            } else {
                // For Ukrainian: show [UKR] entries, hide non-[UKR] entries
                el.style.display = isUkrainianEntry ? 'list-item' : 'none';
            }

            console.log(`A Entry: ${link.innerText}, Display: ${el.style.display}, isUkrainianEntry ${isUkrainianEntry}`);
        });
    }

    // Hide Ukrainian content by default
    document.querySelectorAll('.uk-block').forEach(el => {
        el.style.display = 'none';
    });
    toggleTOC("EN");

    let isEnglish = true;
    
    button.addEventListener('click', function() {
        const enBlocks = document.querySelectorAll('.en-block');
        const ukBlocks = document.querySelectorAll('.uk-block');

        if (isEnglish) {
            enBlocks.forEach(el => el.style.display = 'none');
            ukBlocks.forEach(el => el.style.display = 'block');
            toggleTOC("UKR");
            button.textContent = '🇺🇦';
        } else {
            enBlocks.forEach(el => el.style.display = 'block');
            ukBlocks.forEach(el => el.style.display = 'none');
            toggleTOC("EN");
            button.textContent = '🇺🇸';
        }

        isEnglish = !isEnglish;
    });
});
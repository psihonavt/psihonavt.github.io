document.querySelectorAll('h1').forEach(h1 => {
    if (h1.textContent === '.') {
        h1.style.display = 'none';
    }
});
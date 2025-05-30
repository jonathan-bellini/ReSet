//HTML Load
document.addEventListener('DOMContentLoaded', () => {
    
    //show hide sections
    document.querySelectorAll('.arrow-button').forEach(button => {
        button.addEventListener('click', event => {
            
        const song = button.closest('.song');
        const sections = song.querySelector('.song-sections');

        if (sections) {
            sections.classList.toggle('show');
        }
        });
    });

    document.getElementById('settings').addEventListener('click', function () {
    // Din funktion här
    console.log('Settings klickades!');
    // Eller kör annan kod du vill ska hända
});
});


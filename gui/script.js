//Global Functions
function jumpTo(timeInSeconds) {
fetch('http://127.0.0.1:5000/jump', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json'
    },
    body: JSON.stringify({ timecode: timeInSeconds })
}).then(response => response.json())
    .then(data => console.log(data));
}




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
    document.querySelectorAll('.song-title').forEach(title => {
    title.addEventListener('click', () => {
        // Exempel: hårdkodat timecode, ersätt med riktigt värde
        jumpTo(42.0);
        console.log("click");
        
    });
    });



});


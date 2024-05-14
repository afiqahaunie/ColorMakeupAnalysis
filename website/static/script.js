// Initialize an object to store selected colors
var selectedColors = {
    hair: null,
    skin: null,
    eye: null
};

// Add event listeners for selecting hair, skin, and eye colors
document.getElementById('select-hair-color').addEventListener('click', function() {
    pickColor('hair');
});

document.getElementById('select-skin-color').addEventListener('click', function() {
    pickColor('skin');
});

document.getElementById('select-eye-color').addEventListener('click', function() {
    pickColor('eye');
});

// Function to pick color from canvas
function pickColor(colorType) {
    var canvas = document.getElementById('image-canvas');
    var ctx = canvas.getContext('2d');
    
    // Add event listener to canvas for color selection
    canvas.addEventListener('click', function(event) {
        var x = event.offsetX;
        var y = event.offsetY;
        var pixel = ctx.getImageData(x, y, 1, 1).data;

        // Convert pixel color to hexadecimal
        var colorHex = rgbToHex(pixel[0], pixel[1], pixel[2]);

        // Display selected color
        var colorDiv = document.getElementById(colorType + '-color');
        colorDiv.style.backgroundColor = colorHex;
        colorDiv.textContent = colorHex;

        // Store selected color
        selectedColors[colorType] = colorHex;

        // Remove event listener after color selection
        canvas.removeEventListener('click', arguments.callee);

        console.log('Selected ' + colorType + ' color: ' + colorHex);
    });
}

// Function to convert RGB to hexadecimal color
function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

// Add logic to send selected colors to the server
document.getElementById('generate-palette').addEventListener('click', function() {
    // Check if all colors are selected
    if (selectedColors.hair && selectedColors.skin && selectedColors.eye) {
        // Send selected colors to the server
        fetch('/generate-palette', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(selectedColors)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Log response from server
            displayPalette(data.palette);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
        console.log('Please select hair, skin, and eye colors before generating palette.');
    }
});

// Function to display generated palette
function displayPalette(palette) {
    var paletteColors = document.getElementById('palette-colors');
    paletteColors.innerHTML = ''; // Clear previous palette

    palette.forEach(function(color) {
        var li = document.createElement('li');
        li.style.backgroundColor = color;
        paletteColors.appendChild(li);
    });

    // Show palette section
    document.getElementById('palette-section').style.display = 'block';
}
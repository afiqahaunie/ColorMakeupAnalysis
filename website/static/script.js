window.onload = function() {
    document.getElementById('canvas-section').style.display = 'block';
    var canvas = document.getElementById('image-canvas');
    var ctx = canvas.getContext('2d');
    var img = document.getElementById('uploaded-image');
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
};

// Initialize an object to store selected colors
var selectedColors = {
    hair: null,
    skin: null,
    eye: null
};

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

        // Populate hidden input field with selected color
        var colorInput = document.getElementById(colorType + '-color-input');
        colorInput.value = colorHex;

        // Check if all colors are selected, then show submit button
        if (selectedColors.hair && selectedColors.skin && selectedColors.eye) {
            // Show submit button
            document.getElementById('submit-colors').style.display = 'block';
        }

        console.log('Selected ' + colorType + ' color: ' + colorHex);
    });
}

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

// Function to convert RGB to hexadecimal color
function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

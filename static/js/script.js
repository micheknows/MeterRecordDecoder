// Disable submit button on form submit to prevent double submission
const form = document.querySelector('form');
form.addEventListener('submit', () => {
  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;

  fileInput.value = '';
  alert("Check your downloads for the spreadsheet");
});

// Clear file input after form submission
const fileInput = document.querySelector('#file');
fileInput.addEventListener('change', () => {
  fileInput.value = '';
  alert("Check your downloads for the spreadsheet");
});
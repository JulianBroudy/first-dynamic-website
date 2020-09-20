const signUpButton = document.getElementById('show-signUp');
const signInButton = document.getElementById('show-login');
const container = document.getElementById('forms-wrapper');

signUpButton.addEventListener('click', () => {
  container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
  container.classList.remove("right-panel-active");
});

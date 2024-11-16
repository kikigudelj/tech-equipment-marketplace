document.getElementById('min-price').addEventListener('input', function() {
  document.getElementById('range-value').textContent = this.value + ' € - ' + document.getElementById('max-price').value + ' €';
});

document.getElementById('max-price').addEventListener('input', function() {
  document.getElementById('range-value').textContent = document.getElementById('min-price').value + ' € - ' + this.value + ' €';
});

document.addEventListener('DOMContentLoaded', function() {
  var toastElements = document.querySelectorAll('.toast');
  toastElements.forEach(function(toastElement) {
      var toast = new bootstrap.Toast(toastElement);
      toast.show();
  });

  document.getElementById('registrationForm').addEventListener('submit', function(event) {
      var privacyCheck = document.getElementById('privacyCheck');
      var termsCheck = document.getElementById('termsCheck');
      
      if (!privacyCheck.checked || !termsCheck.checked) {
          event.preventDefault();
          alert('Molimo potvrdite da ste pročitali Politiku privatnosti i prihvatili Uvjete korištenja.');
      }
  });
});
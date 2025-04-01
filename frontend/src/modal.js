document.addEventListener('DOMContentLoaded', function() {
    const employeeModal = document.getElementById('employeeModal');
    if (employeeModal) {
      employeeModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const name = button.getAttribute('data-name');
        const role = button.getAttribute('data-role');
        const image = button.getAttribute('data-image');
        const description = button.getAttribute('data-description') || 'Brak opisu dla tego pracownika.';
        
        const modalTitle = employeeModal.querySelector('#employeeModalLabel');
        const modalRole = employeeModal.querySelector('#employeeRole');
        const modalImage = employeeModal.querySelector('#employeeImage');
        const modalDescription = employeeModal.querySelector('#employeeDescription');
        
        modalTitle.textContent = name;
        modalRole.textContent = role;
        modalImage.src = image;
        modalImage.alt = name;
        modalDescription.textContent = description;
      });
    }
  });
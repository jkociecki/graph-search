document.addEventListener('DOMContentLoaded', function() {
            const mapContainer = document.getElementById('googleMapsContainer');
            mapContainer.style.backgroundColor = '#e9ecef';

            const startInput = document.getElementById('start-location-input');
            const targetInput = document.getElementById('target-location-input');
            const startList = document.getElementById('start-location-list');
            const targetList = document.getElementById('target-location-list');
            const criteriaToggle = document.getElementById('criteria-toggle');
            const submitBtn = document.getElementById('submit-btn');
            const simpleView = document.getElementById('simpleView');
            const resultsView = document.getElementById('results-view');
            const backToForm = document.getElementById('back-to-form');
            const routesContainer = document.getElementById('routes-container');
            


            criteriaToggle.querySelectorAll('button').forEach(button => {
                button.addEventListener('click', function() {
                    criteriaToggle.querySelectorAll('button').forEach(btn => {
                        btn.classList.remove('active');
                        btn.classList.remove('btn-primary');
                        btn.classList.add('btn-outline-primary');
                    });
                    this.classList.add('active');
                    this.classList.add('btn-primary');
                    this.classList.remove('btn-outline-primary');
                });
            });



            document.addEventListener('click', function(e) {
                if (!startInput.contains(e.target) && !startList.contains(e.target)) {
                    startList.classList.remove('show');
                }
                if (!targetInput.contains(e.target) && !targetList.contains(e.target)) {
                    targetList.classList.remove('show');
                }
            });



            submitBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                if (!startInput.value || !targetInput.value) {
                    alert('Proszę wypełnić punkty startowy i docelowy');
                    return;
                }
                handleSubmitButton(e);
                
                simpleView.style.opacity = '0';
                setTimeout(() => {
                    simpleView.style.display = 'none';
                    resultsView.style.display = 'block';
                    setTimeout(() => {
                        resultsView.classList.add('show');
                    }, 50);
                }, 300);
            });

            backToForm.addEventListener('click', function() {
                resultsView.classList.remove('show');
                setTimeout(() => {
                    resultsView.style.display = 'none';
                    simpleView.style.display = 'block';
                    setTimeout(() => {
                        simpleView.style.opacity = '1';
                    }, 50);
                }, 300);
            });
        
        });


        
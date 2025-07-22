// Public Profile Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get current user's skills and profile user's skills from the page
    const currentUserSkills = JSON.parse(document.getElementById('current-user-skills').textContent || '[]');
    const profileUserSkills = JSON.parse(document.getElementById('profile-user-skills').textContent || '[]');
    const profileUserId = document.getElementById('profile-user-id').textContent;
    
    // Populate "Your Skill to Offer" dropdown
    const mySkillSelect = document.getElementById('mySkill');
    mySkillSelect.innerHTML = '<option value="">Select your skill to offer</option>';
    currentUserSkills.forEach(skill => {
        const option = document.createElement('option');
        option.value = skill;
        option.textContent = skill;
        mySkillSelect.appendChild(option);
    });
    
    // Populate "Skill You Want" dropdown
    const theirSkillSelect = document.getElementById('theirSkill');
    theirSkillSelect.innerHTML = '<option value="">Select skill you want</option>';
    profileUserSkills.forEach(skill => {
        const option = document.createElement('option');
        option.value = skill;
        option.textContent = skill;
        theirSkillSelect.appendChild(option);
    });
    
    // Handle form submission
    const requestForm = document.getElementById('requestForm');
    if (requestForm) {
        requestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const mySkill = document.getElementById('mySkill').value;
            const theirSkill = document.getElementById('theirSkill').value;
            const message = document.getElementById('message').value;
            
            // Validate form
            if (!mySkill || !theirSkill) {
                showAlert('Please select both skills for the exchange.', 'error');
                return;
            }
            
            // Prepare request data
            const requestData = {
                to_user_id: profileUserId,
                my_skill: mySkill,
                their_skill: theirSkill,
                message: message
            };
            
            // Send request
            fetch('/send_request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Skill swap request sent successfully!', 'success');
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('requestModal'));
                    if (modal) {
                        modal.hide();
                    }
                    // Reset form
                    requestForm.reset();
                } else {
                    showAlert(data.error || 'Failed to send request. Please try again.', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred while sending the request.', 'error');
            });
        });
    }
    
    // Show alert function
    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of page
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
});

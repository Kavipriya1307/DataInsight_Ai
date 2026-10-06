// =====================================================
// PROFILE DROPDOWN
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    const profileBtn = document.getElementById("profileBtn");
    const dropdown = document.getElementById("profileDropdown");

    if (profileBtn && dropdown) {

        // Toggle dropdown
        profileBtn.addEventListener("click", function (e) {

            e.stopPropagation();

            dropdown.classList.toggle("show");

        });

        // Prevent closing when clicking inside dropdown
        dropdown.addEventListener("click", function (e) {

            e.stopPropagation();

        });

        // Close when clicking outside
        document.addEventListener("click", function () {

            dropdown.classList.remove("show");

        });

    }

});


// =====================================================
// ACTIVE NAVBAR LINK
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    const current = window.location.pathname;

    document.querySelectorAll(".nav-links a").forEach(link => {

        if (link.getAttribute("href") === current) {

            link.classList.add("active");

        }

    });

});
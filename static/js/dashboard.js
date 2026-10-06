/* // ===============================
// PROFILE DROPDOWN
// ===============================

const profileBtn = document.getElementById("profileBtn");
const dropdown = document.getElementById("profileDropdown");

if (profileBtn && dropdown) {

    profileBtn.addEventListener("click", function (e) {

        e.stopPropagation();

        dropdown.classList.toggle("show");

    });

    document.addEventListener("click", function () {

        dropdown.classList.remove("show");

    });

}


// ===============================
// ACTIVE NAVBAR LINK
// ===============================

const currentPage = window.location.pathname;

document.querySelectorAll(".nav-links a").forEach(link => {

    if (link.getAttribute("href") === currentPage) {

        link.classList.add("active");

    }

});
*/

// ===============================
// CARD HOVER EFFECT
// ===============================

document.querySelectorAll(".stat-card").forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-6px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0px)";

    });

});
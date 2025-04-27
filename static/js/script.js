// Ajouter une validation pour le formulaire d'ajout d'une entité
document.addEventListener("DOMContentLoaded", function () {
    const addEntityForm = document.querySelector("form[action='/add']");

    if (addEntityForm) {
        addEntityForm.addEventListener("submit", function (event) {
            const entityType = document.getElementById("entity_type").value;
            const name = document.getElementById("name").value;
            const department = document.getElementById("department");
            const field = document.getElementById("field");
            const course = document.getElementById("course");

            // Validation : Vérifier que le nom n'est pas vide
            if (!name.trim()) {
                event.preventDefault(); // Empêcher la soumission du formulaire
                alert("Veuillez entrer un nom valide.");
                return;
            }

            // Validation spécifique en fonction du type d'entité
            if ((entityType === "Field" || entityType === "Teacher" || entityType === "Researcher") && !department.value.trim()) {
                event.preventDefault();
                alert("Veuillez spécifier un département.");
                return;
            }

            if ((entityType === "Student" || entityType === "Course") && !field.value.trim()) {
                event.preventDefault();
                alert("Veuillez spécifier une filière.");
                return;
            }
        });
    }

    // Ajouter une confirmation avant de supprimer une entité
    const deleteButtons = document.querySelectorAll("form[action^='/delete'] button");
    deleteButtons.forEach((button) => {
        button.addEventListener("click", function (event) {
            const entityName = button.parentElement.parentElement.querySelector("li").textContent.split("\n")[0];
            const confirmDelete = confirm(`Êtes-vous sûr de vouloir supprimer "${entityName}" ?`);
            if (!confirmDelete) {
                event.preventDefault(); // Annuler la suppression si l'utilisateur annule
            }
        });
    });
});
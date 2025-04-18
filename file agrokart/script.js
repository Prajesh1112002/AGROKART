function showSection(sectionId) {
  const sections = document.querySelectorAll('main section');
  sections.forEach(section => {
    section.style.display = 'none';
  });

  const selectedSection = document.getElementById(sectionId);
  if (selectedSection) {
    selectedSection.style.display = 'block';
  }
}

function showCategory(categoryId) {
  const categories = document.querySelectorAll('.product-category');
  categories.forEach(category => {
    category.style.display = 'none';
  });

  const selectedCategory = document.getElementById(categoryId);
  if (selectedCategory) {
    selectedCategory.style.display = 'block';
  }
}

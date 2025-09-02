   const categoryDropdown = document.getElementById('category-select');
   categoryDropdown.addEventListener('change', function () {
      document.getElementById('category-form').submit();
   });
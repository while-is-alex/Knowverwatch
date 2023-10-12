document.getElementById('regions').addEventListener('change', function() {
    localStorage.setItem('selectedRegion', this.value);
    document.getElementById('region-form').submit();
});

document.addEventListener('DOMContentLoaded', function() {
    const selectedRegion = localStorage.getItem('selectedRegion');

    if (selectedRegion) {
        document.getElementById('regions').value = selectedRegion;
    }
});

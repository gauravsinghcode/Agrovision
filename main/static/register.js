AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
});
feather.replace();

function toggleFarmerType(element) {
    document.querySelectorAll('.farmer-type').forEach(el => {
        el.classList.remove('active', 'border-green-600');
        el.classList.add('border-gray-300');
    });
    element.classList.add('active', 'border-green-600');
    element.classList.remove('border-gray-300');
}
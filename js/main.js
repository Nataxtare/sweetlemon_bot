const tabItem = document.querySelectorAll('.tabs_btn-item');
const tabContent = document.querySelectorAll('.tabs_content-item');

tabItem.forEach(function(element) {
    element.addEventListener('click', open);
})

function open(evt){
    const tabTarget = evt.currentTarget;
    const button = tabTarget.dataset.button;

    tabItem.forEach(function(item){
        item.classList.remove('tabs_btn-item-active');
    });

    tabTarget.classList.add('tabs_btn-item-active');

    tabContent.forEach(function(item){
        item.classList.remove('tabs_content-item-active');
    });

    document.querySelector(`#${button}`).classList.add('tabs_content-item-active');
}
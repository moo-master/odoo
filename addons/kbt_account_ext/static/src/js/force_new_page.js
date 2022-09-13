const elem = document.getElementsByClassName("new-page");
const rect = elem[0].getBoundingClientRect();

const data_page_size = elem[0].getAttribute("data_page_size");
const data_page_size_detail = elem[0].getAttribute("data_page_size_detail");

const page_body = document.getElementsByClassName("page_body_set");
const page_size_body = page_body[0].getAttribute("data_body_set");

const page_last = document.getElementsByClassName("last-footer");

// Find data page
const page_data = document.getElementById("data-page")
page_data.innerHTML = elem[0].offset().top
elem.innerHTML = elem.offset().top

if ((rect.top % data_page_size) >= data_page_size_detail) {
    var newdiv = document.getElementsByClassName("new_page");
    newdiv[0].setAttribute('style', 'page-break-after:always');
    size_relative = (Math.ceil(rect.top / data_page_size) + 1) * page_size_body
}
else {
    size_relative = (Math.ceil(rect.top / data_page_size)) * page_size_body
}
page_body[0].style.position = 'relative';
page_body[0].style.height = size_relative + 'mm';
page_last[0].style.position = 'absolute';
page_last[0].style.bottom = '0mm';
page_last[0].style.width = '100%';

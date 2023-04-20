// data-page-size full page without footer
// data-page-size_detail full page with footer
// page-body-set data page check by last line bottom AND top footer

const elem = document.getElementsByClassName("new-page");
// const rect = elem[0].getBoundingClientRect();

const data_page_size = elem[0].getAttribute("data-page-size");
const data_page_size_detail = elem[0].getAttribute("data-page-size-detail");

const page_body = document.getElementsByClassName("page-body-set");
const page_size_body = page_body[0].getAttribute("data-body-set");

const page_last = document.getElementsByClassName("last-footer");

// const counter = parseInt(document.getElementById("data-page").textContent());

const counter = elem[0].getAttribute("count-row");

// Find data page
// const page_data = document.getElementById("data-page")
// page_data.innerHTML = elem[0].getBoundingClientRect().bottom


if ((counter % data_page_size) >= data_page_size_detail) {
    var newdiv = document.getElementsByClassName("new-page");
    newdiv[0].setAttribute('style', 'page-break-after:always');
    size_relative = (Math.ceil(counter / data_page_size) + 1) * page_size_body
}
else {
    size_relative = (Math.ceil(counter / data_page_size)) * page_size_body
}
page_body[0].style.position = 'relative';
page_body[0].style.height = size_relative + 'mm';
page_last[0].style.position = 'absolute';
page_last[0].style.bottom = '0mm';
page_last[0].style.width = '100%';

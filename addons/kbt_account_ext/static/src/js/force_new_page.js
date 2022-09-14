// data-page-size full page without footer
// data-page-size_detail full page with footer
// page-body-set data page check by last line bottom AND top footer

const elem = document.getElementsByClassName("new-page");
const rect = elem[0].getBoundingClientRect();

const data_page_size = elem[0].getAttribute("data-page-size");
const data_page_size_detail = elem[0].getAttribute("data-page-size-detail");

const page_body = document.getElementsByClassName("page-body-set");
const page_size_body = page_body[0].getAttribute("data-body-set");

const page_last = document.getElementsByClassName("last-footer");

// Find data page
// const page_data = document.getElementById("data-page") <= <div class="data-page"/> under LineOrder
// page_data.innerHTML = elem.getBoundingClientRect().top <= print data PageHeight


if ((rect.top % data_page_size) >= data_page_size_detail) {
    var newdiv = document.getElementsByClassName("new-page");
    newdiv[0].setAttribute('style', 'page-break-after:always');
    size_relative = (Math.ceil(rect.top / data_page_size) + 1) * 205
}
else {
    size_relative = (Math.ceil(rect.top / data_page_size)) * 155
}
page_body[0].style.position = 'relative';
page_body[0].style.height = size_relative + 'mm';
page_last[0].style.position = 'static';
page_last[0].style.bottom = '0mm';
page_last[0].style.width = '100%';

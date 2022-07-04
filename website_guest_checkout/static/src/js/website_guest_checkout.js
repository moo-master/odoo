odoo.define('website_guest_checkout.website_guest_checkout', function (require) {
	var ajax = require('web.ajax');
	$(document).ready(function () {
		$('#wk_guest_checkout').on('click', function (event) {
			var uid = $(this).data('uid');
			var p_uid = $(this).data('p_uid');
			if (uid == p_uid) {
				custom_popover(event, $('#div_checkout'), true);
				$('#div_checkout').popover('show');
				if ($(this).data('allow_uninvited') == 'b2c') {
					$('#signup_tab').show();
				}
				event.preventDefault();
			} else {
				$(location).attr('href', '/shop/checkout');
			}
		});
		$('#wk_guest_checkout_main').on('click', function (event) {
			var uid = $(this).data('uid');
			var p_uid = $(this).data('p_uid');
			if (uid == p_uid) {
				custom_popover(event, $('#div_checkout_main'), true);
				$('#div_checkout_main').popover('show');
				if ($(this).data('allow_uninvited') == 'b2c') {
					$('#signup_tab').show();
				}
				event.preventDefault();
			} else {
				$(location).attr('href', '/shop/checkout');
			}
		});
		$('#wk_guest_checkout_main_2').on('click', function (event) {
			var uid = $(this).data('uid');
			var p_uid = $(this).data('p_uid');
			if (uid == p_uid) {
				custom_popover(event, $('#div_checkout_main_2'), true);
				$('#div_checkout_main_2').popover('show');
				if ($(this).data('allow_uninvited') == 'b2c') {
					$('#signup_tab').show();
				}
				event.preventDefault();
			} else {
				$(location).attr('href', '/shop/checkout');
			}
		});
		function custom_popover(event, element_id, status) {
			element_id.popover({
				trigger: 'manual',
				container: 'body',
				template: '<div class="popover guest-checkout-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>',
				placement: 'bottom',
				animation: true,
				html: true,
				sanitize: false,
				content: `<button  id="popover_close" class="close  btn-default float-right" aria-label="Close"><img src="/website_guest_checkout/static/description/layout_close.png"></button>	
								<div class="panel-body text-center wk_guest_checkout_pop">
									<ul class="nav nav-tabs justify-content-center pt-1">
										<li id="login_tab" class="nav-item" style="border-radius:2px;background-color:#d3e0e0;color:#3AADAA;">
											<span href="#check_login" class="nav-link active" role="tab" aria-selected="true" data-toggle="tab">
												Sign In
											</span>
										</li>
										<li id="signup_tab" class="nav-item" style="display:none;border-radius:2px;margin-left:2px;background-color:#d3e0e0;color:#3AADAA;">
											<span href="#check_signup" class="nav-link" role="tab" aria-selected="true" data-toggle="tab">
												Sign Up
											</span>
										</li>
										</ul>
										<div class="tab-content text-center p-0">
											<div id="check_login" class="tab-pane show active fade slow" role="tabpanel">
												<form class="form" role="form">
													<div class="form-group demo_checkout_login_class">
														<label class="guest_email_label float-left mt-1" for="wk_signin_email">Email address</label>
														<input class="form-control" id="wk_signin_email" placeholder="johndoe@demo.com" type="email"/>
													</div>
													<div class="form-group demo_checkout_login_class">
														<label class="guest_psw_label float-left" for="wk_signin_psw">Password</label>
														<input class="form-control" id="wk_signin_psw" placeholder="johndoe@demo.com" type="password"/>
													</div>
													<button id="submit_sign" type="button" class="btn btn-primary float-left mt-1 ml-1" title=""><b>Sign in</b></button>
												</form>
											</div>
											<div id="check_signup" class="tab-pane fade left" role="tabpanel">
												<form class="" role="form">
													<div class="form-group demo_checkout_sign_up_class">
														<label class="name_label float-left mt-1" for="wk_signup_un">User Name</label>
														<input class="form-control" id="wk_signup_un" placeholder="John Doe" type="text"/>
													</div>
													<div class="form-group demo_checkout_sign_up_class">
														<label class="email_label float-left" for="wk_signup_email">Email address</label>
														<input class="form-control" id="wk_signup_email" placeholder="johndoe@demo.com" type="text"/>
													</div>
													<div class="form-group demo_checkout_sign_up_class">
														<label class="password_label float-left" for="wk_signup_psw">Password</label>
														<input class="form-control" id="wk_signup_psw" placeholder="******" type="password"/>
													</div>
													<div class="form-group demo_checkout_sign_up_class">
														<label class="confirm_password_label float-left" for="wk_signup_cpsw">Confirm Password</label>
														<input class="form-control" id="wk_signup_cpsw" placeholder="******" type="password"/>
													</div>
													<button id="submit_signup" type="button" class="btn btn-primary float-left ml-1" title=""><b>Sign up</b></button>
												</form>
											</div>
											<p class="check_login_error py-2"></p>
										</div>
									</div>
								</div>`,

			});
		}

		

		$(document).on('click', '#popover_close', function () {
			$('#div_checkout').popover('hide');
			$('#div_checkout_main').popover('hide');
			$('#div_checkout_main_2').popover('hide');
		});
		$(document).on('click', '#popover_close', function () {
			$('#div_checkout').popover('hide');
		});
		function custom_msg(element_id, status, msg) {
			if (status == true) {
				element_id.empty().append("<div class='alert alert-danger text-center' id='Wk_err'>" + msg + "<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span class='res glyphicon glyphicon-remove ' aria-hidden='true'></span></button></div>");
			}
			if (status == false)
				element_id.empty();
			return true;
		}
		function custom_mark(element_id, status) {
			if (status == true)
				element_id
					.parent()
					.addClass('has-error has-feedback');
		}

		function submitSignIn(){
			var db = $('#wk_database');
			var email = $('#wk_signin_email');
			var psw = $('#wk_signin_psw');
			var input = { login: email.val(), password: psw.val(), db: db.val() };
			ajax.jsonRpc('/checkout/login/', 'call', input)
				.then(function (response) {
					if (response.status) {
						$(location).attr('href', '/shop/checkout');
					}

					else{
						console.log("wk_login_error");
						custom_mark($('.demo_checkout_login_class'), true);
						$('.check_login_error').empty().append(response.message);
					}
				});
		}

		$(document).on('click', '#submit_sign', function () {
			submitSignIn();

		});
		$(document).on('keypress','#wk_signin_email,#wk_signin_psw',function (e) {
			var key = e.which;
			if(key == 13)  // the enter key code
			 {
				 if ($('#wk_signin_email').val() && $('#wk_signin_psw').val()){
					submitSignIn();
				 }
			 }
		   });  
		   
		   function submitSignUp(){

			var name = $('#wk_signup_un');
			var db = $('#wk_database');
			var login = $('#wk_signup_email');
			var password = $('#wk_signup_psw');
			var confirm_password = $('#wk_signup_cpsw');
			var data = {
				'login': login.val(),
				'password': password.val(), confirm_password: confirm_password.val(),
				'db': 'test24',
				name: name.val(),
				redirect: '/shop'
			};
			ajax.jsonRpc('/checkout/signup/', 'call', data)
				.then(function (res) {
					console.log(res);
					if (typeof (res['uid']) != "undefined") {
						$(location).attr('href', '/shop/checkout');
					} else {
						$('.check_login_error').empty().append(res['error']);
						var a = jQuery("#check_signup input:text[value=''] ,#check_signup input:password[value='']");
						a.each(function (index) {
							$(this).parent()
								.addClass('has-error has-feedback')
								.append("<span class='glyphicon glyphicon-remove form-control-feedback'></span>");

						});
					}
				});
		   }

		$(document).on('click', '#submit_signup', function () {
			submitSignUp();
			
		});
		$(document).on('keypress','#wk_signup_un,#wk_signup_email,#wk_signup_psw,#wk_signup_cpsw',function (e) {
			var key = e.which;
			if(key == 13)  // the enter key code
			 {
				 if ($('#wk_signup_un').val() && $('#wk_signup_email').val() && $('#wk_signup_psw').val() && $('#wk_signup_cpsw').val()){
					submitSignUp();
				 }
			 }
		   });  


	});

});

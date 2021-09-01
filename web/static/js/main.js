var coll = document.getElementsByClassName("collapsible");
var i;
for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.maxHeight){
            content.style.maxHeight = null;
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
        }
    });
}

!(function($) {
    "use strict";

    var scrolltoOffset = $('#header').outerHeight() - 1;
$(document).on('click', '.nav-menu a, .mobile-nav a, .scrollto', function(e) {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
        var target = $(this.hash);
        if (target.length) {
            e.preventDefault();

            var scrollto = target.offset().top - scrolltoOffset;

            if ($(this).attr("href") == '#header') {
            scrollto = 0;
            }

            $('html, body').animate({
            scrollTop: scrollto
            }, 1500, 'easeInOutExpo');

            if ($(this).parents('.nav-menu, .mobile-nav').length) {
            $('.nav-menu .active, .mobile-nav .active').removeClass('active');
            $(this).closest('li').addClass('active');
            }

            if ($('body').hasClass('mobile-nav-active')) {
            $('body').removeClass('mobile-nav-active');
            $('.mobile-nav-toggle i').toggleClass('icofont-navigation-menu icofont-close');
            $('.mobile-nav-overly').fadeOut();
            }
            return false;
        }
    }
});

$(document).ready(function() {
    if (window.location.hash) {
    var initial_nav = window.location.hash;
    if ($(initial_nav).length) {
        var scrollto = $(initial_nav).offset().top - scrolltoOffset;
        $('html, body').animate({
        scrollTop: scrollto
        }, 1500, 'easeInOutExpo');
    }
    }
});

var nav_sections = $('section');
var main_nav = $('.nav-menu, #mobile-nav');

$(window).on('scroll', function() {
    var cur_pos = $(this).scrollTop() + 200;

    nav_sections.each(function() {
    var top = $(this).offset().top,
        bottom = top + $(this).outerHeight();

    if (cur_pos >= top && cur_pos <= bottom) {
        if (cur_pos <= bottom) {
        main_nav.find('li').removeClass('active');
        }
        main_nav.find('a[href="#' + $(this).attr('id') + '"]').parent('li').addClass('active');
    }
    if (cur_pos < 300) {
        $(".nav-menu ul:first li:first").addClass('active');
    }
    });
});

$(window).scroll(function() {
    if ($(this).scrollTop() > 100) {
    $('#header').addClass('header-scrolled');
    } else {
    $('#header').removeClass('header-scrolled');
    }
});

if ($(window).scrollTop() > 100) {
    $('#header').addClass('header-scrolled');
}

$(window).scroll(function() {
    if ($(this).scrollTop() > 100) {
    $('.back-to-top').fadeIn('slow');
    } else {
    $('.back-to-top').fadeOut('slow');
    }
});

$('.back-to-top').click(function() {
    $('html, body').animate({
    scrollTop: 0
    }, 1500, 'easeInOutExpo');
    return false;
});

function aos_init() {
    AOS.init({
    duration: 1000,
    easing: "ease-in-out",
    once: true,
    mirror: false
    });
}
$(window).on('load', function() {
    aos_init();
});

})(jQuery);
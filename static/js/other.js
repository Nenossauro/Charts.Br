$(document).ready(function() {

  //FUNCAO DE ABRIR E FECHAR A DIV DE REGISTRO
    $("#btn-register").click(function(event) {
      event.stopPropagation();
  
      $(".registration-div").addClass("entry");
  
      $(document).off("click.registrationDiv").on("click.registrationDiv", function(event) {
          if (!$('.registration-div').is(event.target) && $('.registration-div').has(event.target).length === 0) {
              $('.registration-div').removeClass("entry");
              $(document).off("click.registrationDiv");
          }
      });
  });
  
  //FUNCAO DE ABRIR E FECHAR A DIV DE LOGIN
  $("#btn-login").click(function(event) {
      event.stopPropagation();
  
      $(".login-div").addClass("entry");
  
      $(document).off("click.loginDiv").on("click.loginDiv", function(event) {
          if (!$('.login-div').is(event.target) && $('.login-div').has(event.target).length === 0) {
              $('.login-div').removeClass("entry");
              $(document).off("click.loginDiv");
          }
      });
  });
  
  // ALTERNANCIA DE ABSOLUTE DIV
  $('#R_anchor, #L_anchor').click(function(event) {
    $(".registration-div, .login-div").toggleClass("entry");
  });
  
  // LOADING...
  
    $('.btn-div #btn').click(function(event) {
      $('.loading-page').addClass('show')
    })
    $('.logout-btn #btn').click(function(event) {
      $('.loading-page').addClass('show')
    })
    $('.alter-btn #btn').click(function(event) {
      $('.loading-page').addClass('show')
    })
      // USER CONFIG POP-UP IMG ONCLICK
      $('.user-img').click(function(event) {
  
        
          if($('.config-popup').hasClass("visible")){
            $('.config-popup').removeClass("visible");
          }else{
            $('.config-popup').addClass("visible");
          event.stopPropagation();
          }
      });
          // USER CONFIG POP UP GLOBAL
          $(document).click(function(event) {
              if (!$('.config-popup').is(event.target) && $('.config-popup').has(event.target).length === 0) {
                  $('.config-popup').removeClass("visible");
              }
          });
  
      // DATA DE HOJE - CHECKBOX
      $('#checkbox-date').on('change', function() {
          if ($(this).is(':checked')) {
            const currentDate = new Date();
            const formattedDate = currentDate.toISOString().slice(0, 10);
            $('#input-date').val(formattedDate);
            $('#input-date').prop('disabled', true);
          } else {
            $('#input-date').val('');
            $('#input-date').prop('disabled', false);
          }
        });
  
      // PLUS TOGGLE BUTTON
    
        $('#togglePlusBtn1').on('click', function() {
            var toggle2 = $(this).find('.icon i');
            var inputThird = $('.input-third');
  
            if (toggle2.hasClass('fa-plus')) {
                toggle2.removeClass('fa-plus').addClass('fa-minus');
                inputThird.addClass('show');
            }
            else {
                toggle2.removeClass('fa-minus').addClass('fa-plus');
                inputThird.removeClass('show');
            }
        });
        //APARECER TROCAR SENHA/EMAIL
  
        $('.alterBtn').on('click', function(){
          $('.low-inner-section-div').addClass('after')
        })
  
        //VOLTAR PRA PAGINA ANTERIOR
        $('#goBack').on('click', function(){
          history.back()
        })
  
        //IR PARA A HOME
        $('.logo').on('click', function() {
          window.location.href = '/land';
        });
  
        //IR PARA CRIE SUA CHART
        $('.new-chart').on('click', function(){
          window.location.href = '/criar-chart';
        })
  
        //IR PARA RESPONDER PERGUNTAS
        $('.answer-chart').on('click', function(){
          window.location.href = '/adicionar-informações';
        })
  
  
        //TOGGLE DARK MODE
        $('#toggle-dark-mode').click(function(){
  
          $('body').toggleClass('dark-mode');
  
          if ($('body').hasClass('dark-mode')) {
            localStorage.setItem('dark-mode', 'enabled');
            $('#logo').attr("src", "/static/charts.logoDARK.png");
          } else {
            localStorage.setItem('dark-mode', 'disabled');
            $('#logo').attr("src", "/static/charts.logo.png");
          }
        });
  
        const darkModePreference = localStorage.getItem('dark-mode');
        if (darkModePreference === 'enabled') {
          $('#logo').attr("src", "/static/charts.logoDARK.png");
          $('body').addClass('dark-mode');
        }
  });
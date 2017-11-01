this.ckan.module('add_package_typed', function ($, _) {
  var modal;
  var self;

  function initialize() {
    self = this;
    modal = $('#embed-add_package_typed')
    this.el.on('click', _onClick);
    $('form', modal).submit(function(event){
        var package_type = $("select[name=package_type]").val();
        console.log("submit: ", package_type);
        location.href = "" + package_type + "/new/";
        event.preventDefault();
    });
  }

  function _onClick (event) {
    event.preventDefault();
    modal.modal('show');
  }

  function _preventClick (event) {
    event.preventDefault();
  }

  return {
    initialize: initialize,
    options: {
      id: 0,
      url: '#',
      width: 700,
      height: 400
    }
  }
});

/*
    Initializes the TinyMCE editor.
*/


tinyMCE.init({
    mode: "specific_textareas",
    theme: "advanced",
    editor_selector: "html",
    plugins: "table, advimage, media, inlinepopups",
    theme_advanced_buttons1: "code,|,formatselect,styleselect,|,bullist,numlist,table,|,bold,italic,|,sub,sup,|,link,unlink,image,media",
    theme_advanced_buttons2: "",
    theme_advanced_buttons3: "",
    width: "700px",
    height: "350px",
    dialog_type: "modal",
    theme_advanced_blockformats: "h2,h3,p",
    external_link_list_url: "{% url tinymce_link_list %}",
    external_image_list_url: "{% url tinymce_image_list %}",
    content_css: "{{TINYMCE_CONTENT_CSS}}",
    extended_valid_elements : "iframe[src|width|height|name|align]",
    convert_urls: false
});


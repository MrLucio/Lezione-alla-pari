$('#title-editor').attr('contenteditable', 'true');

let temp_content = $("#content-editor").html();
$("#content-editor").html('');

console.log($("#content-editor").html())

let quill = new Quill('#content-editor', {
    modules: {
      'toolbar': [
        [{ 'font': [] }, { 'size': [] }],
        [ 'bold', 'italic', 'underline', 'strike' ],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'script': 'super' }, { 'script': 'sub' }],
        [{ 'header': '1' }, { 'header': '2' }, 'blockquote', 'code-block' ],
        [{ 'list': 'ordered' }, { 'list': 'bullet'}, { 'indent': '-1' }, { 'indent': '+1' }],
        /*[ 'direction', { 'align': [] }],
        [ 'link', 'image', 'video', 'formula' ],
        [ 'clean' ]*/
      ]
    },
    placeholder: 'Compose an epic...',
    theme: 'snow'  // or 'bubble'
});

quill.clipboard.dangerouslyPasteHTML(temp_content, 'api')

// SANITIZE HTML WITH dangerouslyPasteHTML FROM QUILL
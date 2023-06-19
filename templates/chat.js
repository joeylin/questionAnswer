document.getElementById('send-button').addEventListener('click', function() {
  var input = document.getElementById('message-input');
  var message = input.value;

  var chatBox = document.getElementById('chat-box');

  var sentMessageElement = document.createElement('div');
  sentMessageElement.textContent = message;
  sentMessageElement.className = 'message message-sent';
  chatBox.appendChild(sentMessageElement);

  fetch('/query', {  // 后端的API接口
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({query: message})
  })
  .then(response => response.json())
  .then(data => {
    $('#chatbody').append('<p><strong>Server:</strong> ' + data.msg + '</p>');

//    var receivedMessageElement = document.createElement('div');
//    receivedMessageElement.textContent = '回复：' + data.msg;
//    receivedMessageElement.className = 'message message-received';
//    chatBox.appendChild(receivedMessageElement);
//    chatBox.scrollTop = chatBox.scrollHeight;
  });
});

document.getElementById('file-upload').addEventListener('change', function(e) {
  var file = e.target.files[0];

  var formData = new FormData();
  formData.append('file', file);

  fetch('/upload', {  // 后端的API接口
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    var chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += '<p>已上传文件: ' + data.fileName + '</p>';
    chatBox.scrollTop = chatBox.scrollHeight;
  });
});
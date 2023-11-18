document.getElementById('gradeForm').addEventListener('submit', function (event) {
    event.preventDefault(); // 防止表单默认的提交行为

    const className = document.getElementById('className').value;

    // 使用 Fetch API 或其他 AJAX 方法将数据发送到后端
    fetch('http://127.0.0.1:5000/api/grade/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: className }), // 将用户输入的数据转换为 JSON 字符串
    })
        .then(response => response.json())
        .then(data => {
            // 处理后端返回的响应
            console.log('Data saved successfully:', data);
        })
        .catch(error => {
            console.error('Error saving data:', error);
        });
});
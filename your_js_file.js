document.addEventListener('DOMContentLoaded', function () {
    // 在页面加载完成后执行这段代码

    // 使用 Fetch API 发起 GET 请求获取数据
    fetch('http://127.0.0.1:5000/apis/grade/')
        .then(response => response.json())
        .then(data => {
            // 成功获取数据后的处理
            displayData(data.data);
        })
        .catch(error => {
            // 请求发生错误的处理
            console.error('Error fetching data:', error);
        });
});

// 渲染数据到页面
function displayData(grades) {
    const gradesListDiv = document.getElementById('grades-list');

    // 清空现有内容
    gradesListDiv.innerHTML = '';

    // 遍历数据并渲染到页面
    grades.forEach(grade => {
        const gradeDiv = document.createElement('div');
        gradeDiv.textContent = `Class ID: ${grade.id}, Class Name: ${grade.name}`;
        gradesListDiv.appendChild(gradeDiv);
    });
}
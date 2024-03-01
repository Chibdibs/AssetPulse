document.getElementById("fetchData").addEventListener("click", function() {
    fetch('/protected-resource')
        .then(response => response.json())
        .then(data => {
            document.getElementById("accountInfo").innerText = JSON.stringify(data, null, 2);
        })
        .catch(error => console.error('Error fetching data:', error));
});

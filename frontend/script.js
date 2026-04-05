async function analyze() {
  const url = document.getElementById("url").value;

  const res = await fetch("YOUR_BACKEND_URL/geo-audit", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ url })
  });

  const data = await res.json();

  document.getElementById("output").innerText =
    JSON.stringify(data, null, 2);
}

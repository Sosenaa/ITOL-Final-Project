

document.addEventListener("DOMContentLoaded", () => {
     const orderSelected = document.getElementById("date-order");
     const statusOrder = document.getElementById("status");
     const title = document.getElementsByClassName("search-by-title");

     if (orderSelected){
          orderSelected.addEventListener("change", (e) => {
               sortByDate(e.target.value);
          });
     }

     if(statusOrder){
          statusOrder.addEventListener("change",(e)=> {
               sortByStatus(e.target.value);
          });
     }

     Array.from(title).forEach(input => {
     input.addEventListener("input", e => {
          const query = e.target.value
               .replace(/\s+/g, "")
               .toLowerCase();

          searchByTitle(query);
          });
     });
});

function getTaskRows(){
     return Array.from(document.querySelectorAll("#details-container div.grid"));
}

function renderRows(rows){
     const tasksList = document.getElementById("details-container");
     tasksList.innerHTML = "";
     rows.forEach(row => tasksList.appendChild(row));
}

function sortByDate(order){
     const rows = getTaskRows();

     rows.sort((a,b) => {
          const dateA = new Date(a.children[2].textContent.trim()).getTime();
          const dateB = new Date(b.children[2].textContent.trim()).getTime();

          return order === "Date Ascending" ? dateA - dateB : dateB - dateA;
     });
     renderRows(rows);
}

function sortByStatus(status){
     const rows = getTaskRows();

     rows.sort((a,b) => {
          const statusA = a.children[3].textContent.trim();
          const statusB = b.children[3].textContent.trim();

          if(statusA === status && statusB !== status) return -1;
          if(statusA !== status && statusB === status) return 1;
          return 0;
          console.log(rows);
     });
     renderRows(rows);
}

let currentSearch = "";

function searchByTitle(title){
     currentSearch = title;

     getTaskRows().forEach(row =>{
          const text = row.children[0].textContent
          .toLowerCase()
          .replace(/\s+/g,'');

          row.style.display = text.includes(title) ? "" : "none";
     });
}
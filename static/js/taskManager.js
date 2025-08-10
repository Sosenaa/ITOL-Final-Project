

document.addEventListener("DOMContentLoaded", () => {
     const orderSelected = document.getElementById("date-order");
     const statusOrder = document.getElementById("status");
     const title = document.getElementById("search-by-title");

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

     if(title){
          title.addEventListener("input", (e)=>{
               const query = title.value.replace(/\s+/g,'').toLowerCase();
               searchByTitle(query);
               console.log(query);
          });
     }

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

function searchByTitle(title){
     const rows = getTaskRows();

     rows.sort((a,b) =>{
          const statusA = a.children[0].textContent.replace(/\s+/g,'').toLowerCase();
          const statusB = b.children[0].textContent.replace(/\s+/g,'').toLowerCase();

          if(statusA === title && statusB !== title) return -1;
          if(statusA !== title && statusB === title) return 1;
          return 0;
          console.log(rows);
     })
     renderRows(rows);
}
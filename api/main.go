package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	_ "github.com/mattn/go-sqlite3"
)

type H map[string]any

var DB *sql.DB

type Record struct {
	Subsidiary   string  `json:"subsidiary"`
	Title        string  `json:"title"`
	Author       string  `json:"author"`
	Currency_iso string  `json:"currency_iso"`
	Total_mrr    float32 `json:"total_mrr"`
	Data         string  `json:"data"`
}

func post_api_enpoint(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var rec Record
	err := json.NewDecoder(r.Body).Decode(&rec)
	if err != nil {
		w.WriteHeader(400)
		json.NewEncoder(w).Encode(H{"status": "error", "error": err.Error()})
		log.Printf("%s", err.Error())
	} else {
		fmt.Printf("MRR is %f\n", rec.Total_mrr)

		result, err := DB.Exec("INSERT INTO record (subsidiary, title, author, currency_iso, total_mrr, data) VALUES (?, ?, ?, ?, ?, ?)",
			rec.Subsidiary, rec.Title, rec.Author, rec.Currency_iso, rec.Total_mrr, rec.Data)
		if err != nil {
			log.Println(err.Error())
		} else {
			id, _ := result.LastInsertId()
			json.NewEncoder(w).Encode(H{"status": "ok", "id": id})
		}
	}
}

func get_api_endpoint(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(H{"status": "ok"})
}

func main() {
	var err error
	DB, err = sql.Open("sqlite3", "./foo.db")
	if err != nil {
		log.Fatal(err)
	}
	defer DB.Close()

	mux := http.NewServeMux()
	mux.HandleFunc("POST /api-endpoint", post_api_enpoint)
	mux.HandleFunc("GET /api-endpoint", get_api_endpoint)
	log.Fatal(http.ListenAndServe(":8080", mux))
}

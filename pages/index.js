import Head from 'next/head'
import { useState, useMemo } from 'react';
import {search} from "backend/search";

export default function Home() {
  const [isFocused, setIsFocused] = useState(false);
  const headerClassName = isFocused
        ? "header wide"
        : "header";
  
  const eventHandlers = useMemo(() => ({
    onFocus: () => setIsFocused(true),
    onBlur: () => setIsFocused(false),
  }), []);

  const keyPressHandler = (e) => {
    if (e.key === "Enter") {
      search(e.target.value)
        .then(response => setResults(response.data))
        .catch(error => {console.log("error"); console.log(JSON.stringify(error))}
      );    
    }
  }

  const [results, setResults] = useState([]);
    
  return (
    <div className="container">
      <Head>
        <title>Spidey Search</title>
        <link rel="icon" href="/favicon.ico" />
        <link rel="stylesheet" href="/style.css" />
      </Head>

      <main>
        <div id="app">
          <div className={headerClassName}>
            <div className="titleContainer">
              <h1 className="title">Spidey Search</h1>
            </div>
            <div className="searchBarContainer">
              <input className='searchBar' placeholder="Search" {...eventHandlers} onKeyPress={keyPressHandler} />
            </div>
          </div>
          <div className="results">
            {
             
                results.map( result =>
                    <div key={result.id} className="search-result">
                        <div>
                          <a href={result.url}>{result.title}</a>
                        </div>
                        <div>
                          <a href={result.url}>{result.url}</a>
                        </div>
                    </div>
                )       
              
              }
          </div>
        </div>
      </main>
    </div>
  )
}

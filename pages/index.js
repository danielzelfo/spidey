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
      if (e.target.value === "") {
        setAppStyle("glass");
        setResults([])
      } else {
        setAppStyle("dark");
        search(e.target.value)
          .then(response => setResults(response.data))
          .catch(error => {console.log("error"); console.log(JSON.stringify(error))}
        );
      }
      
      
    }
  }

  const [results, setResults] = useState([]);

  const [appStyle, setAppStyle] = useState("glass");
    
  return (
    <div className="container">
      <Head>
        <title>Spidey Search</title>
        <link rel="icon" href="/favicon.ico" />
        <link rel="stylesheet" href="/style.css" />
      </Head>

      <main>
        <div id="app" className={appStyle}>
          <div className={headerClassName}>
            <div className="titleContainer">
              <h1 className="title"><span>S</span><span>p</span><span>i</span><span>d</span><span>e</span><span>y</span> Search</h1>
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

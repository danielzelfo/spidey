import Head from 'next/head'
import { useState, useMemo } from 'react';

export default function Home() {
  const [isFocused, setIsFocused] = useState(false);
  const headerClassName = isFocused
        ? "header wide"
        : "header";
  
  const eventHandlers = useMemo(() => ({
    onFocus: () => setIsFocused(true),
    onBlur: () => setIsFocused(false),
  }), []);

  const [results, setResults] = useState([
    {"title": "Department of Statistics - Donald Bren School of Information & Computer Sciences – Department of Statistics - Donald Bren School of Information & Computer Sciences", "url": "https://www.stat.uci.edu"},
    {"title": "Informatics @ the University of California, Irvine", "url": "https://www.informatics.uci.edu"},
    {"title": "Donald Bren School of Information and Computer Sciences @ University of California, Irvine", "url": "https://www.ics.uci.edu"},
    {"title": "Department of Computer Science - Donald Bren School of Information & Computer Sciences – Department of Computer Science - Donald Bren School of Information & Computer Sciences", "url": "https://www.cs.uci.edu"},
    {"title": "Home | UCI Mathematics", "url": "https://www.math.uci.edu"}
  ]);
    
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
              <input className='searchBar' {...eventHandlers} placeholder="Search" />
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

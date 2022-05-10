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
          </div>
        </div>
      </main>
    </div>
  )
}

import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import * as d3 from 'd3';

function App() {
  const [data, setData] = useState([]);
  const [selected, setSelected] = useState(null);
  const svgRef = useRef();

  const loadData = () => {
    // Usamos el puerto 8000 de tu FastAPI
    axios.get('http://127.0.0.1:8000/api/noticias')
      .then(res => {
        // Mapeamos los datos por si vienen vacíos o con nombres distintos
        const formattedData = res.data.map(d => ({
          ...d,
          // Si no hay impacto, le damos un tamaño base de 40
          radius: 40, 
          // Ajustamos sentimiento a lo que manda la IA (POS, NEG, NEU)
          tipo: d.sentiment 
        }));
        setData(formattedData);
      })
      .catch(err => console.error("Servidor Mac desconectado"));
  };

  useEffect(() => {
    loadData();
    // Bajamos el intervalo a 5 segundos para que sea casi "tiempo real"
    const interval = setInterval(loadData, 5000); 
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!data.length) return;

    const width = window.innerWidth;
    const height = window.innerHeight - 150;
    const svg = d3.select(svgRef.current).attr('width', width).attr('height', height);
    svg.selectAll("*").remove();

    const simulation = d3.forceSimulation(data)
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('charge', d3.forceManyBody().strength(30))
      // Colisión basada en el radio que definimos
      .force('collide', d3.forceCollide(d => 45)) 
      .on('tick', () => {
        node.attr('transform', d => `translate(${d.x},${d.y})`);
      });

    const node = svg.selectAll('.node')
      .data(data)
      .enter().append('g')
      .attr('class', 'node')
      .on('mouseover', (e, d) => setSelected(d))
      .style('cursor', 'pointer');

    // Círculos con el color del sentimiento de la IA
    node.append('circle')
      .attr('r', 40)
      .attr('fill', 'rgba(10, 10, 10, 0.8)')
      .attr('stroke', d => {
        if (d.sentiment === 'POS') return '#00ff88'; // Verde
        if (d.sentiment === 'NEG') return '#ff3333'; // Rojo
        return '#00d4ff'; // Azul para Neutro/X
      })
      .attr('stroke-width', 3)
      .style('filter', 'drop-shadow(0 0 5px rgba(0,212,255,0.3))');

    // Texto corto adentro de la burbuja (Sentimiento)
    node.append('text')
      .attr('dy', '4')
      .style('text-anchor', 'middle')
      .style('fill', '#fff')
      .style('font-size', '10px')
      .style('font-weight', 'bold')
      .text(d => d.sentiment);

  }, [data]);

  return (
    <div style={{ background: '#050505', color: '#fff', minHeight: '100vh', fontFamily: 'monospace', overflow: 'hidden' }}>
      <div style={{ padding: '20px', background: '#000', borderBottom: '1px solid #1a1a1a', display: 'flex', justifyContent: 'space-between' }}>
        <div>
          <span style={{ color: '#00ff88', fontWeight: 'bold', fontSize: '1.2rem' }}>X_SENTIMENT_RADAR</span>
          <div style={{ color: '#444', fontSize: '0.7rem' }}>CONECTADO_A_MAC_SERVER</div>
        </div>

        {selected && (
          <div style={{ maxWidth: '600px', borderLeft: '3px solid #00ff88', paddingLeft: '15px' }}>
            <div style={{ fontSize: '0.7rem', color: '#00ff88' }}>{selected.date} | {selected.sentiment}</div>
            <div style={{ fontSize: '1rem', color: '#eee', lineHeight: '1.2' }}>{selected.title}</div>
          </div>
        )}
      </div>

      <svg ref={svgRef}></svg>
      
      <div style={{ position: 'fixed', bottom: 10, right: 20, color: '#00ff88', fontSize: '0.6rem', opacity: 0.5 }}>
        LIVE_FEED_ACTIVE // {data.length} NOTICIAS_PROCESADAS
      </div>
    </div>
  );
}

export default App;
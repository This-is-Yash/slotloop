import React,{useEffect,useState}from"react";
import{Search,MapPin,Clock,Store,ArrowUpRight,LayoutDashboard,Plus,RefreshCw,X,CheckCircle2}from"lucide-react";
// const api=async(p,o={})=>{const r=await fetch("/api"+p,{headers:{"Content-Type":"application/json"},...o});const d=await r.json();if(!r.ok)throw Error(d.detail||"Request failed");return d};
const API_BASE = "http://127.0.0.1:8000";

const api = async (p, o = {}) => {
  const r = await fetch(`${API_BASE}/api${p}`, {
    ...o,
    headers: {
      "Content-Type": "application/json",
      ...o.headers
    }
  });

  const contentType = r.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    const responseText = await r.text();
    throw new Error(
      `Expected JSON but received ${r.status}: ${responseText.slice(0, 150)}`
    );
  }

  const d = await r.json();

  if (!r.ok) {
    throw new Error(d.detail || "Request failed");
  }

  return d;
};
const money=n=>"₹"+Number(n||0).toLocaleString("en-IN");
const dt=s=>new Date(s).toLocaleString("en-IN",{day:"numeric",month:"short",hour:"numeric",minute:"2-digit"});
export default function App(){
 const[tab,T]=useState("discover"),[items,I]=useState([]),[biz,B]=useState([]),[service,S]=useState("Haircut"),[area,A]=useState("Andheri"),[budget,U]=useState("500"),[err,E]=useState(""),[msg,M]=useState(""),[chosen,C]=useState(null),[name,N]=useState("Demo Customer"),[email,Q]=useState("customer@example.com"),[id,D]=useState("1"),[dash,H]=useState(null);
 const[f,F]=useState({starts_at:"2026-11-02T17:00",ends_at:"2026-11-02T17:45",price:"350",original_price:"550"});
 async function search(){try{E("");I(await api("/slots?"+new URLSearchParams({service,area,max_price:budget})));}catch(e){E(e.message)}}
 async function loadBiz(){try{B(await api("/businesses"))}catch(e){E(e.message)}}
 async function loadDash(){try{H(await api(`/businesses/${id}/dashboard`))}catch(e){E(e.message)}}
 useEffect(()=>{loadBiz();search()},[]);
 useEffect(()=>{if(tab==="business")loadDash()},[tab,id]);
 async function book(){try{await api("/bookings",{method:"POST",body:JSON.stringify({slot_id:chosen.id,customer_name:name,customer_email:email})});C(null);M("Demo booking confirmed. No payment was collected.");search();loadDash()}catch(e){E(e.message)}}
 async function publish(e){e.preventDefault();try{await api(`/businesses/${id}/slots`,{method:"POST",body:JSON.stringify({...f,price:+f.price,original_price:+f.original_price})});M("Availability published.");loadDash();search()}catch(e){E(e.message)}}
 const field=(k,v)=>(e)=>F({...f,[k]:e.target.value});
 return <><header><b className="logo">S<span>·</span> SLOTLOOP</b><nav><button onClick={()=>T("discover")} className={tab==="discover"?"active":""}><Search size={15}/> Discover</button><button onClick={()=>T("business")} className={tab==="business"?"active":""}><LayoutDashboard size={15}/> Business studio</button></nav><small>● DEMO ENVIRONMENT</small></header><main><section className="hero"><label>THE CAPACITY MARKETPLACE</label><h1>Don't let good business<br/><em>go to waste.</em></h1><p>Find last-minute local availability — or turn empty business hours into revenue.</p></section><aside>ⓘ Fictional seed listings for demonstration only. This is not live business inventory.</aside>{err&&<p className="alert">{err}<button onClick={()=>E("")}>×</button></p>}{msg&&<p className="success">{msg}<button onClick={()=>M("")}>×</button></p>}
 {tab==="discover"?<section className="section"><label className="kicker">FOR CUSTOMERS</label><h2>Find your next free slot.</h2><div className="filters"><label>Service<select value={service} onChange={e=>S(e.target.value)}>{["Haircut","Hair colouring","Nail appointment","Badminton court"].map(x=><option>{x}</option>)}</select></label><label>Area<input value={area} onChange={e=>A(e.target.value)}/></label><label>Max budget<input type="number" value={budget} onChange={e=>U(e.target.value)}/></label><button className="primary" onClick={search}><Search size={16}/> Find availability</button></div><div className="heading"><h3>Available opportunities</h3><button onClick={search}><RefreshCw size={14}/> Refresh</button></div><div className="cards">{items.map(s=><article key={s.id}><div className="pill">AVAILABLE · {s.discount_percent}% OFF</div><h3>{s.business_name}</h3><p><Store/> {s.service}</p><p><MapPin/> {s.area} · {s.address}</p><div className="time"><Clock/> {dt(s.starts_at)}</div><div className="bottom"><b>{money(s.price)} <del>{money(s.original_price)}</del></b><button className="primary" onClick={()=>C(s)}>Book <ArrowUpRight size={15}/></button></div></article>)}{!items.length&&<p className="empty">No matching demo slots. Try a different service, area or budget.</p>}</div></section>:<section className="section"><label className="kicker">FOR BUSINESS OWNERS</label><h2>Turn empty time into income.</h2><label className="selectbiz">Demo business<select value={id} onChange={e=>D(e.target.value)}>{biz.map(b=><option value={b.id}>{b.name} — {b.service}</option>)}</select></label>{dash&&<><div className="metrics"><div><small>Recovered demo revenue</small><b>{money(dash.metrics.recovered_revenue)}</b></div><div><small>Bookings recovered</small><b>{dash.metrics.recovered_bookings||0}</b></div><div><small>Available slots</small><b>{dash.metrics.available_slots||0}</b></div></div><div className="business"><form onSubmit={publish}><h3>Publish availability</h3><label>Start<input type="datetime-local" value={f.starts_at} onChange={field("starts_at")}/></label><label>End<input type="datetime-local" value={f.ends_at} onChange={field("ends_at")}/></label><div className="two"><label>Offer price<input type="number" value={f.price} onChange={field("price")}/></label><label>Usual price<input type="number" value={f.original_price} onChange={field("original_price")}/></label></div><button className="primary"><Plus size={16}/> Publish slot</button></form><div className="inventory"><h3>Your availability</h3>{dash.slots.map(s=><p><span>{dt(s.starts_at)} · {money(s.price)}</span><b className={"status "+s.status}>{s.status}</b></p>)}</div></div></>}</section>}
 <section className="how"><label className="kicker">THE BIG IDEA</label><h2>Capacity is inventory.<br/>Time is the expiry date.</h2><div><article><b>01</b><h3>Businesses publish</h3><p>Expose availability that would otherwise expire unused.</p></article><article><b>02</b><h3>Customers discover</h3><p>Match flexible demand to service, location and price.</p></article><article><b>03</b><h3>Revenue gets recovered</h3><p>Turn unused capacity into measurable bookings.</p></article></div></section><footer><b>SLOTLOOP</b><span>Prototype · No live inventory or payments</span></footer></main>
 {chosen&&<div className="overlay" onClick={()=>C(null)}><div className="modal" onClick={e=>e.stopPropagation()}><button className="x" onClick={()=>C(null)}><X/></button><label className="kicker">DEMO BOOKING</label><h2>{chosen.business_name}</h2><p>{chosen.service} · {dt(chosen.starts_at)} · {money(chosen.price)}</p><label>Your name<input value={name} onChange={e=>N(e.target.value)}/></label><label>Email<input type="email" value={email} onChange={e=>Q(e.target.value)}/></label><aside>Demo only. No payment or real appointment is created.</aside><button className="primary wide" onClick={book}><CheckCircle2/> Confirm demo booking</button></div></div>}</>}

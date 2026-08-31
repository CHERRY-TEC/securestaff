import express from 'express';
import cors from 'cors';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import multer from 'multer';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'rbm-security-telangana-2026-secret';

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Ensure dirs
if (!fs.existsSync(path.join(__dirname, 'uploads'))) fs.mkdirSync(path.join(__dirname, 'uploads'));
if (!fs.existsSync(path.join(__dirname, 'data'))) fs.mkdirSync(path.join(__dirname, 'data'));

const DB_PATH = path.join(__dirname, 'data', 'db.json');

// Init DB
function loadDB(){
  if(!fs.existsSync(DB_PATH)){
    const init = {
      users: [
        // Seeded company admin - phone 9949811742 / password: rbm@2026  (also OTP 123456)
        {id: 'company-admin-001', phone: '+919949811742', name: 'RBM Security Company', role: 'Company', isCompany: true, createdAt: new Date().toISOString()},
        {id: 'company-admin-002', phone: '+918897535830', name: 'RBM Admin', role: 'Admin', isCompany: true, createdAt: new Date().toISOString()}
      ],
      jobs: [
        {id:1, cat:'guard', title:'Residential Security Guard', company:'DLF Magnolias', loc:'Hyderabad • Gachibowli', salary:'₹22k - ₹28k', type:'Full-time • 8h shift', tags:['Immediate Joining','Food + Stay'], verified:true, hot:true, applicants:47, img:'https://images.unsplash.com/photo-1580894906475-403276d45aed?q=80&w=400&auto=format&fit=crop', createdAt: new Date().toISOString()},
        {id:2, cat:'cctv', title:'CCTV Control Room Operator', company:'Taj Palace Hotel', loc:'Hyderabad • Banjara Hills', salary:'₹26k - ₹35k', type:'Night Shift • 12h', tags:['5-Star Hotel','PF + Insurance'], verified:true, applicants:32, img:'https://images.unsplash.com/photo-1557597774-9d273605dfa9?q=80&w=400&auto=format&fit=crop', createdAt: new Date().toISOString()},
        {id:3, cat:'housekeeping', title:'Housekeeping Staff — 5 Star Hotel', company:'The Leela Palace', loc:'Hyderabad • Banjara Hills', salary:'₹18k - ₹24k', type:'Full-time • 8h shift', tags:['Hotel','Food + Stay','PF'], verified:true, hot:true, applicants:73, img:'https://images.unsplash.com/photo-1581578731548-c64695cc6952?q=80&w=400&auto=format&fit=crop', createdAt: new Date().toISOString()},
        {id:4, cat:'wardboy', title:'Ward Boy — Fortis Hospital', company:'Fortis Memorial', loc:'Hyderabad • Secunderabad', salary:'₹17k - ₹25k', type:'Hospital • 12h', tags:['Patient Care','Training Provided'], verified:true, applicants:38, img:'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?q=80&w=400&auto=format&fit=crop', createdAt: new Date().toISOString()},
        {id:5, cat:'helper', title:'Office Helper / Peon', company:'HDFC Bank HQ', loc:'Hyderabad • Begumpet', salary:'₹15k - ₹20k', type:'Full-time • 10h', tags:['Bank','Office Work'], verified:true, applicants:62, img:'https://images.unsplash.com/photo-1521737711867-e3b97375f902?q=80&w=400&auto=format&fit=crop', createdAt: new Date().toISOString()},
        {id:6, cat:'manpower', title:'Manpower Supply — 50 Workers Urgent', company:'L&T Construction Site', loc:'Hyderabad • Patancheru', salary:'₹15k - ₹23k', type:'Bulk • 50 Workers', tags:['BULK 50','Urgent','Site Work'], verified:true, hot:true, applicants:156, img:'https://images.unsplash.com/photo-1541888946425-d81bb19240f6?q=80&w=400&auto=format&fit=crop', createdAt: new Date().toISOString()},
      ],
      applications: [],
      otps: {} // phone -> {code, expires}
    };
    fs.writeFileSync(DB_PATH, JSON.stringify(init, null, 2));
  }
  const db = JSON.parse(fs.readFileSync(DB_PATH, 'utf-8'));
  // Ensure company users exist even if DB already existed (migration)
  let changed = false;
  const companySeeds = [
    {id: 'company-admin-001', phone: '+919949811742', name: 'RBM Security Company', role: 'Company', isCompany: true},
    {id: 'company-admin-002', phone: '+918897535830', name: 'RBM Admin', role: 'Admin', isCompany: true}
  ];
  for(const seed of companySeeds){
    if(!db.users.find(u=> u.id===seed.id || u.phone===seed.phone)){
      db.users.push({...seed, createdAt: new Date().toISOString()});
      changed = true;
    } else {
      // ensure isCompany flag
      const u = db.users.find(u=> u.id===seed.id || u.phone===seed.phone);
      if(u && !u.isCompany){ u.isCompany = true; changed = true; }
      if(u && !u.role.includes('Company') && !u.role.includes('Admin')){ /* keep role */ }
    }
  }
  if(changed) fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
  return db;
}
function saveDB(db){
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

// Multer for file uploads (photo, ID)
const storage = multer.diskStorage({
  destination: (req,file,cb)=> cb(null, path.join(__dirname, 'uploads')),
  filename: (req,file,cb)=> cb(null, Date.now()+'-'+file.originalname.replace(/\s/g,'_'))
});
const upload = multer({ storage, limits:{fileSize: 5*1024*1024} });

// Auth middleware
function auth(req,res,next){
  const h = req.headers.authorization;
  if(!h) return next(); // allow optional
  const token = h.split(' ')[1];
  if(!token) return next();
  try{
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
  }catch(e){}
  next();
}
function requireAuth(req,res,next){
  if(!req.user) return res.status(401).json({error:'Unauthorized - Please login'});
  next();
}
// Company-only auth - tracker is company private
function requireCompanyAuth(req,res,next){
  if(!req.user) return res.status(401).json({error:'Company login required'});
  const role = (req.user.role || '').toLowerCase();
  const isCompany = role.includes('company') || role.includes('admin') || role.includes('employer') || role.includes('owner') || req.user.isCompany === true;
  if(!isCompany) return res.status(403).json({error:'Company access only - tracker is private'});
  next();
}
const COMPANY_ROLES = ['Company','Admin','Employer','Owner'];

// HEALTH
app.get('/api/health', (req,res)=> res.json({ok:true, service:'RBM Security Backend', telangana:true, time: new Date().toISOString()}));

// AUTH
app.post('/api/auth/send-otp', (req,res)=>{
  const {phone, name, role} = req.body;
  if(!phone) return res.status(400).json({error:'Phone required'});
  const code = '123456'; // demo fixed, in prod use Twilio
  const db = loadDB();
  db.otps[phone] = {code, expires: Date.now()+5*60*1000, name, role};
  saveDB(db);
  console.log(`[OTP] ${phone} -> ${code}`);
  res.json({ok:true, message:'OTP sent (demo 123456)', code}); // return code for demo
});

app.post('/api/auth/verify-otp', async (req,res)=>{
  const {phone, code, name, role} = req.body;
  const db = loadDB();
  const otp = db.otps[phone];
  if(!otp || otp.code !== code || Date.now() > otp.expires){
    return res.status(400).json({error:'Invalid or expired OTP'});
  }
  // find or create user
  let user = db.users.find(u=> u.phone===phone);
  if(!user){
    const hashed = await bcrypt.hash(phone, 8); // not used but placeholder
    const isCompany = (role||'').toLowerCase().includes('company') || (role||'').toLowerCase().includes('admin');
    user = {id: uuidv4(), phone, name: name || otp.name || 'RBM User', role: role || otp.role || 'Job Seeker — Guard', isCompany: isCompany, createdAt: new Date().toISOString()};
    db.users.push(user);
  }
  delete db.otps[phone];
  saveDB(db);
  const token = jwt.sign({id:user.id, phone:user.phone, name:user.name, role:user.role, isCompany: !!user.isCompany}, JWT_SECRET, {expiresIn:'30d'});
  res.json({ok:true, token, user});
});

app.post('/api/auth/login', async (req,res)=>{
  // legacy: direct login without OTP for demo
  const {phone} = req.body;
  const db = loadDB();
  let user = db.users.find(u=> u.phone===phone);
  if(!user) return res.status(404).json({error:'User not found, please register'});
  const token = jwt.sign({id:user.id, phone:user.phone, name:user.name, role:user.role, isCompany: !!user.isCompany}, JWT_SECRET, {expiresIn:'30d'});
  res.json({ok:true, token, user});
});

// COMPANY LOGIN - tracker private access only
app.post('/api/auth/company-login', async (req,res)=>{
  const {phone, password, code} = req.body;
  const db = loadDB();
  // Allow OTP 123456 for company phones OR password rbm@2026
  const COMPANY_PHONES = ['+919949811742','9949811742','+918897535830','8897535830'];
  const COMPANY_PASSWORD = 'rbm@2026';
  const normalizedPhone = phone ? phone.replace(/\s/g,'') : '';
  const isCompanyPhone = COMPANY_PHONES.some(p=> p.replace(/\s/g,'') === normalizedPhone || normalizedPhone.endsWith(p.slice(-10)));
  if(code === '123456' && isCompanyPhone){
    let user = db.users.find(u=> u.phone===normalizedPhone || u.phone.slice(-10)===normalizedPhone.slice(-10));
    if(!user){
      user = {id: uuidv4(), phone: normalizedPhone, name: 'RBM Security Company', role: 'Company', isCompany: true, createdAt: new Date().toISOString()};
      db.users.push(user); saveDB(db);
    }
    const token = jwt.sign({id:user.id, phone:user.phone, name:user.name, role:user.role, isCompany: true}, JWT_SECRET, {expiresIn:'30d'});
    return res.json({ok:true, token, user});
  }
  if(password === COMPANY_PASSWORD && isCompanyPhone){
    let user = db.users.find(u=> u.phone===normalizedPhone || u.phone.slice(-10)===normalizedPhone.slice(-10));
    if(!user){
      user = {id: uuidv4(), phone: normalizedPhone, name: 'RBM Security Company', role: 'Company', isCompany: true, createdAt: new Date().toISOString()};
      db.users.push(user); saveDB(db);
    }
    const token = jwt.sign({id:user.id, phone:user.phone, name:user.name, role:user.role, isCompany: true}, JWT_SECRET, {expiresIn:'30d'});
    return res.json({ok:true, token, user});
  }
  return res.status(401).json({error:'Invalid company credentials. Use company phone + OTP 123456 or password rbm@2026'});
});

// Verify company token
app.get('/api/auth/company-me', auth, requireCompanyAuth, (req,res)=>{
  res.json({ok:true, user:req.user, isCompany:true});
});

app.get('/api/auth/me', auth, (req,res)=>{
  if(!req.user) return res.status(401).json({error:'No token'});
  const db = loadDB();
  const user = db.users.find(u=> u.id===req.user.id);
  res.json({ok:true, user});
});

// JOBS
app.get('/api/jobs', (req,res)=>{
  const db = loadDB();
  let jobs = [...db.jobs];
  // filters
  const {cat, city, search, minSalary, sort} = req.query;
  if(cat && cat!=='all') jobs = jobs.filter(j=> j.cat===cat);
  if(city) jobs = jobs.filter(j=> j.loc.toLowerCase().includes(city.toLowerCase()));
  if(search){
    const q = search.toLowerCase();
    jobs = jobs.filter(j=> j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q) || j.loc.toLowerCase().includes(q));
  }
  if(minSalary){
    const min = parseInt(minSalary);
    jobs = jobs.filter(j=> {
      const m=j.salary.match(/(\d+)[kK]/);
      const sal=m? parseInt(m[1])*1000 : 0;
      return sal >= min;
    });
  }
  if(sort==='salaryHigh') jobs.sort((a,b)=> (b.salary.match(/(\d+)[kK]/)?.[1]||0) - (a.salary.match(/(\d+)[kK]/)?.[1]||0));
  if(sort==='salaryLow') jobs.sort((a,b)=> (a.salary.match(/(\d+)[kK]/)?.[1]||0) - (b.salary.match(/(\d+)[kK]/)?.[1]||0));
  res.json({ok:true, jobs});
});

app.post('/api/jobs', auth, requireCompanyAuth, (req,res)=>{
  const db = loadDB();
  const {title, company, cat, loc, city, salary, type, tags, img} = req.body;
  if(!title || !company) return res.status(400).json({error:'title/company required'});
  const job = {
    id: Date.now(),
    cat: cat||'guard',
    title, company,
    loc: loc || (city ? city+' • Telangana' : 'Hyderabad • Telangana'),
    salary: salary||'₹18k - ₹28k',
    type: type||'Full-time • 8h',
    tags: Array.isArray(tags)? tags : (tags ? tags.split(',').map(s=>s.trim()) : ['New Posting']),
    verified:true, hot:true, applicants: Math.floor(Math.random()*20)+1,
    img: img || 'https://images.unsplash.com/photo-1580894906475-403276d45aed?q=80&w=400&auto=format&fit=crop',
    createdAt: new Date().toISOString(),
    postedBy: req.user?.id || null
  };
  db.jobs.unshift(job);
  saveDB(db);
  res.json({ok:true, job});
});

app.delete('/api/jobs/:id', auth, requireCompanyAuth, (req,res)=>{
  const db = loadDB();
  const id = parseInt(req.params.id);
  db.jobs = db.jobs.filter(j=> j.id !== id);
  saveDB(db);
  res.json({ok:true});
});

// APPLICATIONS - COMPANY ONLY (tracker private)
app.get('/api/applications', auth, requireCompanyAuth, (req,res)=>{
  const db = loadDB();
  let apps = [...db.applications];
  const {city, job, search, date} = req.query;
  if(city) apps = apps.filter(a=> a.city===city);
  if(job) apps = apps.filter(a=> a.jobTitle.toLowerCase().includes(job.toLowerCase()));
  if(search){
    const q=search.toLowerCase();
    apps = apps.filter(a=> [a.name,a.phone,a.city,a.jobTitle].join(' ').toLowerCase().includes(q));
  }
  if(date==='today'){
    const today=new Date().toDateString();
    apps = apps.filter(a=> new Date(a.date).toDateString()===today);
  }
  res.json({ok:true, applications: apps});
});

app.post('/api/applications', upload.fields([{name:'photo', maxCount:1}, {name:'idFile', maxCount:1}]), (req,res)=>{
  const db = loadDB();
  let body = req.body;
  // handle JSON as well as multipart
  const name = body.name;
  const phone = body.phone;
  const city = body.city;
  const exp = body.exp;
  const docs = body.docs;
  const jobTitle = body.jobTitle;
  if(!name || !phone) return res.status(400).json({error:'name/phone required'});
  let photoUrl = null;
  if(req.files && req.files.photo && req.files.photo[0]){
    photoUrl = '/uploads/'+req.files.photo[0].filename;
  } else if(body.photo){ // base64
    // save base64 as file if provided
    if(body.photo.startsWith('data:image')){
      const base64 = body.photo.split(',')[1];
      const filename = Date.now()+'-photo.jpg';
      const fp = path.join(__dirname, 'uploads', filename);
      fs.writeFileSync(fp, Buffer.from(base64, 'base64'));
      photoUrl = '/uploads/'+filename;
    } else {
      photoUrl = body.photo;
    }
  }
  const app = {
    id: Date.now(),
    name, phone, city: city||'Hyderabad', exp: exp||'Fresher',
    docs: docs||'Aadhaar',
    jobTitle: jobTitle||'General Application',
    date: new Date().toISOString(),
    status: 'New',
    photo: photoUrl,
    idFile: req.files?.idFile ? '/uploads/'+req.files.idFile[0].filename : null
  };
  db.applications.unshift(app);
  saveDB(db);
  res.json({ok:true, application: app});
});

app.patch('/api/applications/:id/status', auth, requireCompanyAuth, (req,res)=>{
  const db = loadDB();
  const id = parseInt(req.params.id);
  const {status} = req.body;
  const app = db.applications.find(a=> a.id===id);
  if(!app) return res.status(404).json({error:'Not found'});
  app.status = status;
  saveDB(db);
  res.json({ok:true, application: app});
});

app.delete('/api/applications/:id', auth, requireCompanyAuth, (req,res)=>{
  const db = loadDB();
  const id = parseInt(req.params.id);
  db.applications = db.applications.filter(a=> a.id!==id);
  saveDB(db);
  res.json({ok:true});
});

app.delete('/api/applications', auth, requireCompanyAuth, (req,res)=>{
  const db = loadDB();
  db.applications = [];
  saveDB(db);
  res.json({ok:true});
});

// STATS - COMPANY ONLY
app.get('/api/stats', auth, requireCompanyAuth, (req,res)=>{
  const db = loadDB();
  const total = db.applications.length;
  const today = db.applications.filter(a=> new Date(a.date).toDateString()===new Date().toDateString()).length;
  const cityMap={}; db.applications.forEach(a=> cityMap[a.city]=(cityMap[a.city]||0)+1);
  const topCity = Object.entries(cityMap).sort((a,b)=>b[1]-a[1])[0] || ['Hyderabad',0];
  const jobMap={}; db.applications.forEach(a=> jobMap[a.jobTitle]=(jobMap[a.jobTitle]||0)+1);
  const topJob = Object.entries(jobMap).sort((a,b)=>b[1]-a[1])[0] || ['—',0];
  res.json({ok:true, total, today, topCity, topJob, totalJobs: db.jobs.length, totalUsers: db.users.length});
});

// Serve frontend static - TWO SEPARATE WEBSITES
// 1. Company public site (client) at / - for everyone: jobs, apply, view company info
// 2. Tracker dashboard (company private) at /tracker - for company staff only
const clientPath = fs.existsSync(path.join(__dirname, '../client')) ? path.join(__dirname, '../client') : path.join(__dirname, '../securehire');
const trackerPath = fs.existsSync(path.join(__dirname, '../tracker')) ? path.join(__dirname, '../tracker') : path.join(__dirname, '../rbm-tracker');

// Public company site - no auth needed
app.use(express.static(clientPath));

// Tracker - static files are served, but API data requires company auth (see requireCompanyAuth above)
// Frontend will show login gate if not company - true separation is at API level
app.use('/tracker', express.static(trackerPath));

// Also serve /applications.html as company-only view (legacy local dashboard)
// It will be gated on frontend via company auth check
app.get('/applications.html', (req,res)=>{
  const p = path.join(clientPath, 'applications.html');
  if(fs.existsSync(p)) res.sendFile(p);
  else res.status(404).send('Not found');
});

app.get('/tracker/*', (req,res)=>{
  // Serve tracker index for SPA routes within tracker
  const p = path.join(trackerPath, 'index.html');
  if(fs.existsSync(p)) res.sendFile(p);
  else res.status(404).send('Tracker not found');
});

app.get('*', (req,res)=>{
  // fallback to client index.html for SPA
  const p = path.join(clientPath, 'index.html');
  if(fs.existsSync(p)) res.sendFile(p);
  else res.status(404).send('Not found');
});

app.listen(PORT, ()=> console.log(`✅ RBM Security Backend running at http://localhost:${PORT}\n   API: http://localhost:${PORT}/api/health\n   Frontend: http://localhost:${PORT}/\n   Tracker: http://localhost:${PORT}/tracker`));

import { Link, NavLink } from "react-router-dom";

const Signup = () => {
 return (
     <div className="min-h-[90vh] w-full bg-stone-200 flex items-center justify-center p-6 caret-transparent ">
       <div className="w-full max-w-md bg-stone-300 rounded-2xl shadow-xl p-8 md:p-10">
         {/* Logo */}
         <div className="flex items-center   mb-6">
            <img src="/autoims.png" alt="AutoIMS Logo" className="w-16 h-16" />
           <span className="text-2xl font-bold text-gray-900">
             AutoIMS
           </span>
         </div>
 
         <p className="mt-1 text-sm text-gray-700 font-semibold">Manage your Services.</p>
            <form className="mt-6 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input label="Full name" placeholder="John Cena" />
                  <Input label="Username" placeholder="John" />
                </div>

                <Input
                  label="Email Address"
                  type="email"
                  placeholder="john@example.com"
          
                />
                <Input
                  label="Password"
                  type="password"
                  placeholder="••••••••"
                />

                <button
                  type="button"
                  className="w-full mt-2 rounded-xl bg-indigo-700 py-3 text-sm font-semibold cursor-pointer tracking-wide text-white shadow-lg transition hover:-translate-y-0.5"
                >
                  CREATE AN ACCOUNT
                </button>
              </form>

              <p className="mt-6 text-xs text-slate-500 text-center">
                Already have an account?{" "}
                <Link
                  to="/login"
                  className="text-blue-600 font-semibold cursor-pointer hover:underline"
                >
                  Login
                </Link>
              </p>
         
       </div>
     </div>
   );
 };

const Input = ({ label, type = "text", placeholder }) => {
  return (
    <div>
      <label className="block mb-1.5 text-xs font-semibold text-slate-500">
        {label}
      </label>
      <input
        type={type}
        placeholder={placeholder}
        className="w-full h-11 rounded-xl border border-indigo-100 bg-indigo-50/60 px-4 text-sm text-slate-800 outline-none transition focus:border-indigo-300 focus:shadow-md"
      />
    </div>
  );
};

export default Signup;

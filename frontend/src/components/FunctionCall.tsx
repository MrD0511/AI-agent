// import { useState } from "react";
// import { FunctionCall } from "../types/chat";
// import { ChevronDown, ChevronUp, Play, Code } from "lucide-react";

// type Props = {
//   functionCall: FunctionCall;
// };

// const FunctionCallItem: React.FC<Props> = ({ functionCall }) => {
//   const [isOpen, setIsOpen] = useState(false);

//   return (
//     <div className="w-full bg-gray-100 dark:bg-gray-800/80 rounded-lg overflow-hidden mb-3 border border-gray-200 dark:border-gray-700 shadow-sm">
//       {/* Header */}
//       <div
//         className="cursor-pointer flex justify-between items-center p-3 hover:bg-gray-200 dark:hover:bg-gray-700/50 transition-colors"
//         onClick={() => setIsOpen(!isOpen)}
//       >
//         <div className="flex items-center gap-2">
//           <div className="bg-primary/20 dark:bg-primary-dark/20 p-1.5 rounded-full">
//             <Code className="h-4 w-4 text-primary dark:text-primary-dark" />
//           </div>
//           <span className="font-medium text-gray-800 dark:text-gray-200">{functionCall.name}</span>
//         </div>
//         <button className="text-gray-500 hover:text-gray-800 dark:hover:text-gray-200 transition-colors">
//           {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
//         </button>
//       </div>

//       {/* Expanded Content */}
//       {isOpen && (
//         <div className="border-t border-gray-200 dark:border-gray-700">
//           {/* Arguments Section */}
//           <div className="p-3">
//             <div className="flex items-center gap-2 mb-2">
//               <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Arguments</span>
//               <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700"></div>
//             </div>
//             <pre className="bg-white dark:bg-gray-900 p-3 rounded-md text-xs text-gray-800 dark:text-gray-200 overflow-x-auto">
//               {JSON.stringify(functionCall.arguments, null, 2)}
//             </pre>
//           </div>
          
//           {/* Execute Button (if applicable) */}
//           {functionCall.canExecute && (
//             <div className="p-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
//               <button className="w-full py-2 bg-primary dark:bg-primary-dark text-white rounded-md flex items-center justify-center gap-2 hover:bg-primary/90 dark:hover:bg-primary-dark/90 transition-colors">
//                 <Play className="h-4 w-4" />
//                 <span>Execute Function</span>
//               </button>
//             </div>
//           )}
//         </div>
//       )}
//     </div>
//   );
// };

// export default FunctionCallItem;
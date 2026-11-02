// Audited availability, not an anatomical completeness score or expert approval.
export const coverageReference='https://training.seer.cancer.gov/anatomy/nervous/organization/cns.html';
export const nervousCoverage=[
 {key:'brain',state:'partial',fr:'Encéphale : plusieurs structures disponibles',en:'Brain: selected structures available',ar:'الدماغ: تتوفر بعض البنى'},
 {key:'cranial',state:'partial',fr:'Nerfs crâniens : représentation partielle',en:'Cranial nerves: partial representation',ar:'الأعصاب القحفية: تمثيل جزئي'},
 {key:'cord',state:'missing',fr:'Moelle épinière complète',en:'Complete spinal cord',ar:'الحبل الشوكي الكامل',terms:['spinal cord','moelle épinière','medulla spinalis','الحبل الشوكي']},
 {key:'spinal',state:'missing',fr:'Nerfs spinaux et racines',en:'Spinal nerves and roots',ar:'الأعصاب الشوكية وجذورها',terms:['spinal nerves','nerfs spinaux','nerfs rachidiens']},
 {key:'plexus',state:'missing',fr:'Plexus brachial et lombo-sacré',en:'Brachial and lumbosacral plexuses',ar:'الضفيرتان العضدية والقطنية العجزية',terms:['brachial plexus','plexus brachial','lumbosacral plexus']},
 {key:'limbs',state:'missing',fr:'Grands nerfs des membres : médian, ulnaire, sciatique…',en:'Major limb nerves: median, ulnar, sciatic…',ar:'الأعصاب الرئيسية للأطراف: المتوسط والزندي والوركي',terms:['median nerve','nerf médian','ulnar nerve','nerf ulnaire','sciatic nerve','nerf sciatique','radial nerve','nerf radial','femoral nerve','nerf fémoral','tibial nerve','العصب المتوسط','العصب الزندي','العصب الوركي']},
 {key:'autonomic',state:'unreviewed',fr:'Réseaux autonomes : couverture non validée',en:'Autonomic networks: coverage not validated',ar:'الشبكات الذاتية: التغطية غير معتمدة'}
];
export const medicalReleaseStatus={ready:false,anatomicalReviewer:null,reason:'Incomplete nervous anatomy and unreviewed system classification'};

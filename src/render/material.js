import {MeshStandardMaterial,DoubleSide} from 'three';

// BodyParts3D packs may omit NORMAL. GLTFLoader then uses flat shading;
// replacing its material must first supply normals for smooth anatomical shading.
export function anatomyMaterial(geometry,color){
 if(!geometry.getAttribute('normal'))geometry.computeVertexNormals();
 const normals=geometry.getAttribute('normal');
 let flatShading=false;
 for(let i=0;i<normals.count;i++){
  const length=Math.hypot(normals.getX(i),normals.getY(i),normals.getZ(i));
  if(!Number.isFinite(length)||length<.5){flatShading=true;break;}
 }
 return new MeshStandardMaterial({color,roughness:.66,metalness:.02,side:DoubleSide,flatShading});
}

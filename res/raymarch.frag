#version 330

precision highp float;

uniform float time;
uniform vec2 resolution;
uniform vec2 touch;

#define COLORS 7
#define INTERSECT 200
#define SOFT_SHADOW 40
#define AOI 5

//#define POINT_LIGHT


//========================================================================================
// matrix operations
// https://github.com/dsheets/gloc/blob/master/stdlib/matrix.glsl
//========================================================================================

// constructors are column major 
mat2 transpose(mat2 m) {
  return mat2(  m[0][0], m[1][0],
                m[0][1], m[1][1]
             );
  }

mat3 transpose(mat3 m) {
  return mat3(  m[0][0], m[1][0], m[2][0],
                m[0][1], m[1][1], m[2][1],
                m[0][2], m[1][2], m[2][2]
             );
  }

mat4 transpose(mat4 m) {
  return mat4(  m[0][0], m[1][0], m[2][0], m[3][0],
                m[0][1], m[1][1], m[2][1], m[3][1],
                m[0][2], m[1][2], m[2][2], m[3][2],
                m[0][3], m[1][3], m[2][3], m[3][3]
             );
  }

float det(mat2 m) {
  return m[0][0]*m[1][1] - m[1][0]*m[0][1] ;
  }

float det(mat3 m) {
  return   m[0][0]*( m[1][1]*m[2][2] - m[2][1]*m[1][2])
         - m[1][0]*( m[0][1]*m[2][2] - m[2][1]*m[0][2])
         + m[2][0]*( m[0][1]*m[1][2] - m[1][1]*m[0][2]) ;
  }

float det(mat4 m) {
  mat2 a = mat2(m);
  mat2 b = mat2(m[2].xy,m[3].xy);
  mat2 c = mat2(m[0].zw,m[1].zw);
  mat2 d = mat2(m[2].zw,m[3].zw);
  float s = det(a);
  return s*det(d-(1.0/s)*c*mat2(a[1][1],-a[0][1],-a[1][0],a[0][0])*b);
  }

mat2 inv(mat2 m) {
  return mat2( m[1][1], -m[0][1], -m[1][0], m[0][0]) / det(m) ;
  }

mat3 inv(mat3 m) {
  return     mat3(  m[2][2]*m[1][1] - m[1][2]*m[2][1],
                    m[1][2]*m[2][0] - m[2][2]*m[1][0],
                    m[2][1]*m[1][0] - m[1][1]*m[2][0] ,

                    m[0][2]*m[2][1] - m[2][2]*m[0][1],
                    m[2][2]*m[0][0] - m[0][2]*m[2][0],
                    m[0][1]*m[2][0] - m[2][1]*m[0][0],
   
                    m[1][2]*m[0][1] - m[0][2]*m[1][1],
                    m[0][2]*m[1][0] - m[1][2]*m[0][0],
                    m[1][1]*m[0][0] - m[0][1]*m[1][0]
                 ) / det(m);
  }

mat4 inv(mat4 m) {
  mat2 a = inv(mat2(m));
  mat2 b = mat2(m[2].xy,m[3].xy);
  mat2 c = mat2(m[0].zw,m[1].zw);
  mat2 d = mat2(m[2].zw,m[3].zw);

  mat2 t = c*a;
  mat2 h = inv(d - t*b);
  mat2 g = - h*t;
  mat2 f = - a*b*h;
  mat2 e = a - f*t;

  return mat4(  vec4(e[0],g[0]), vec4(e[1],g[1]), 
                vec4(f[0],h[0]), vec4(f[1],f[1]) );
  }

//========================================================================================
// rotation
// http://www.neilmendoza.com/glsl-rotation-about-an-arbitrary-axis/
//========================================================================================

mat3 rotationMatrix(vec3 axis, float angle)
{
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
    
    return mat3(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,
                oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,
                oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c);
}

vec3 rotate(vec3 p, vec3 axis, float angle)
{
    mat3 rot = rotationMatrix(axis,angle);
    return rot*p;
}

vec3 rotateAroundPoint(vec3 p, vec3 anchor, vec3 axis, float angle)
{
    return rotate(p-anchor,axis,angle)+anchor;   
}

vec3 invrotate(vec3 p, vec3 axis, float angle)
{
    mat3 rot = inv(rotationMatrix(axis,angle));
    return rot*p;
}

vec3 invrotateAroundPoint(vec3 p, vec3 anchor, vec3 axis, float angle)
{
    return invrotate(p-anchor,axis,angle)+anchor;   
}

// https://www.shadertoy.com/view/4sXXRN
// https://www.shadertoy.com/view/4slSWf

//========================================================================================
// noises
//========================================================================================

float hash( float n )
{
    return fract(sin(n)*43758.5453123);
}

float noise( in vec2 x )
{
    vec2 p = floor(x);
    vec2 f = fract(x);
    f = f*f*(3.0-2.0*f);
    float n = p.x + p.y*157.0;
    return mix(mix( hash(n+  0.0), hash(n+  1.0),f.x),
               mix( hash(n+157.0), hash(n+158.0),f.x),f.y);
}

const mat2 m2 = mat2( 0.80, -0.60, 0.60, 0.80 );

float fbm( vec2 p )
{
    float f = 0.0;
    f += 0.5000*noise( p ); p = m2*p*2.02;
    f += 0.2500*noise( p ); p = m2*p*2.03;
    f += 0.1250*noise( p ); p = m2*p*2.01;
    f += 0.0625*noise( p );
    return f/0.9375;
}

//========================================================================================
// distance primitives
//========================================================================================

float sdBox( vec3 p, vec3 b )
{
  vec3 d = abs(p) - b;
  return min(max(d.x,max(d.y,d.z)),0.0) + length(max(d,0.0));
}

vec2 sdSegment( vec3 a, vec3 b, vec3 p )
{
    vec3 pa = p - a;
    vec3 ba = b - a;
    float h = clamp( dot(pa,ba)/dot(ba,ba), 0.0, 1.0 );
    
    return vec2( length( pa - ba*h ), h );
}

float sdCone( in vec3 p, in vec3 c )
{
    vec2 q = vec2( length(p.xz), p.y );
    return max( max( dot(q,c.xy), p.y), -p.y-c.z );
}

float sdSphere( vec3 p, float s )
{
    return length(p)-s;
}

float sdTorus( vec3 p, vec2 t )
{
  vec2 q = vec2(length(p.xz)-t.x,p.y);
  return length(q)-t.y;
}

float sdCylinder( vec3 p, vec2 h )
{
  vec2 d = abs(vec2(length(p.xz),p.y)) - h;
  return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

float udRoundBox( vec3 p, vec3 b, float r )
{
  return length(max(abs(p)-b,0.0))-r;
}

float sdPlane( vec3 p, vec3 n, float d )
{
  return dot(p,n) + d;
}

float det( vec2 a, vec2 b ) { return a.x*b.y-b.x*a.y; }
vec3 getClosest( vec2 b0, vec2 b1, vec2 b2 ) 
{
    
  float a =     det(b0,b2);
  float b = 2.0*det(b1,b0);
  float d = 2.0*det(b2,b1);
  float f = b*d - a*a;
  vec2  d21 = b2-b1;
  vec2  d10 = b1-b0;
  vec2  d20 = b2-b0;
  vec2  gf = 2.0*(b*d21+d*d10+a*d20); gf = vec2(gf.y,-gf.x);
  vec2  pp = -f*gf/dot(gf,gf);
  vec2  d0p = b0-pp;
  float ap = det(d0p,d20);
  float bp = 2.0*det(d10,d0p);
  float t = clamp( (ap+bp)/(2.0*a+b+d), 0.0 ,1.0 );
  return vec3( mix(mix(b0,b1,t), mix(b1,b2,t),t), t );
}

vec2 sdBezier( vec3 a, vec3 b, vec3 c, vec3 p, in float thickness )
{
    vec3 w = normalize( cross( c-b, a-b ) );
    vec3 u = normalize( c-b );
    vec3 v = normalize( cross( w, u ) );

    vec2 a2 = vec2( dot(a-b,u), dot(a-b,v) );
    vec2 b2 = vec2( 0.0 );
    vec2 c2 = vec2( dot(c-b,u), dot(c-b,v) );
    vec3 p3 = vec3( dot(p-b,u), dot(p-b,v), dot(p-b,w) );

    vec3 cp = getClosest( a2-p3.xy, b2-p3.xy, c2-p3.xy );

    return vec2( 0.85*(sqrt(dot(cp.xy,cp.xy)+p3.z*p3.z) - thickness), cp.z );
}

float dot2( in vec3 v ) { return dot(v,v); }

float udTriangle( in vec3 v1, in vec3 v2, in vec3 v3, in vec3 p )
{
    vec3 v21 = v2 - v1; vec3 p1 = p - v1;
    vec3 v32 = v3 - v2; vec3 p2 = p - v2;
    vec3 v13 = v1 - v3; vec3 p3 = p - v3;
    vec3 nor = cross( v21, v13 );

    return sqrt( (sign(dot(cross(v21,nor),p1)) + 
                  sign(dot(cross(v32,nor),p2)) + 
                  sign(dot(cross(v13,nor),p3))<2.0) 
                  ?
                  min( min( 
                  dot2(v21*clamp(dot(v21,p1)/dot2(v21),0.0,1.0)-p1), 
                  dot2(v32*clamp(dot(v32,p2)/dot2(v32),0.0,1.0)-p2) ), 
                  dot2(v13*clamp(dot(v13,p3)/dot2(v13),0.0,1.0)-p3) )
                  :
                  dot(nor,p1)*dot(nor,p1)/dot2(nor) );
}

//========================================================================================
// distance operators
//========================================================================================

// polynomial smooth min
float smin( float a, float b, float k )
{
    float h = clamp( 0.5+0.5*(b-a)/k, 0.0, 1.0 );
    return mix( b, a, h ) - k*h*(1.0-h);
}

// union
float opU( float d1, float d2 ) { return min( d1,d2); }
vec3  opU( vec3  d1, vec3  d2 ) { return vec3(opU(d1.x,d2.x),opU(d1.y,d2.y),opU(d1.z,d2.z)); }
// subtraction
float opS( float d2, float d1 ) { return max(-d1,d2); }
vec3  opS( vec3  d2, vec3  d1 ) { return vec3(opS(d2.x,d1.x),opS(d2.y,d1.y),opS(d2.z,d1.z)); }
// intersection
float opI( float d1, float d2 ) { return max(d1,d2); } 
vec3  opI( vec3  d1, vec3  d2 ) { return vec3(opI(d1.x,d2.x),opI(d1.y,d2.y),opI(d1.z,d2.z)); }

// repetition
vec3  opRep( vec3  p,  vec3  c  ) { return mod(p,c)-0.5*c; } 

// morph
float opMorph( float d1, float d2, float a) { return a*d1 + (1.0-a)*d2; }

// scaling
vec3 opInvScale(vec3 p, vec3 scale) { return p / scale; }
float opScale(float d, vec3 scale) { return d * min(scale.x,min(scale.y,scale.z)); }

struct Intersection
{
    float t,id;
};

float round(Intersection is1, Intersection is2, float t)
{
    float m = 0.5*(is1.t+is2.t);
    return (m>is1.t && t<m)?is1.id:is2.id;
}

Intersection opU( Intersection is1, Intersection is2)
{
    float t = opU(is1.t,is2.t);
    float id = round(is1,is2,t);
    return Intersection(t,id);
}

Intersection opS( Intersection is2, Intersection is1)
{
    float t = opS(is2.t,is1.t);
    float id = round(is1,is2,t);
    return Intersection(t,id);
}

Intersection smin( Intersection is1, Intersection is2, float k)
{
    float t = smin(is1.t,is2.t,k);
    float id = round(is1,is2,t);
    return Intersection(t,id);
}

Intersection map( in vec3 p );

Intersection intersect( in vec3 ro, in vec3 rd )
{
    const float maxd = 100.0;
    Intersection h = Intersection(0.1,0.0);
    float t = 0.0;
    for( int i=0; i<INTERSECT; i++ )
    {
        if( h.t<0.0001 ||t > maxd ) break;
        h = map( ro+rd*t );
        t += h.t;
    }

    if( t>maxd ) t=-1.0;
    
    return Intersection(t,h.id);
}

float calcSoftshadow( in vec3 ro, in vec3 rd, float k )
{
    float res = 1.0;
    float t = 0.0;
    float h = 1.0;
    for( int i=0; i<SOFT_SHADOW; i++ )
    {
        h = map(ro + rd*t).t;
        res = min( res, k*h/t );
        t += clamp( h, 0.001, 1.0 );
        if( h<0.0001 ) break;
    }
    return clamp(res,0.0,1.0);
}

float calcOcclusion( in vec3 pos, in vec3 nor )
{
    float ao = 1.0;
    float totao = 0.0;
    float sca = 1.0;
    for( int aoi=0; aoi<AOI; aoi++ )
    {
        float hr = 0.02 + 0.025*float(aoi*aoi);
        vec3 aopos =  nor * hr + pos;
        float dd = map( aopos ).t;
        totao += -(dd-hr)*sca;
        sca *= 0.95;
    }
    return 1.0 - clamp( totao, 0.0, 1.0 );
}

void generateRay( out vec3 resRo, out vec3 resRd, in vec3 po, in vec3 ta, in vec2 pi )
{
    vec2 p = (-resolution.xy + 2.0*pi)/resolution.y;
        
    // camera matrix
    vec3 ww = normalize( ta - po );
    vec3 uu = normalize( cross(ww,vec3(0.0,1.0,0.0) ) );
    vec3 vv = normalize( cross(uu,ww));

    // create view ray
    vec3 rd = normalize( p.x*uu + p.y*vv + 2.2*ww );

    resRo = po;
    resRd = rd;
}

vec3 calcNormal( in vec3 pos )
{
    vec3 eps = vec3(0.005,0.0,0.0);
    return normalize( vec3( map(pos+eps.xyy).t - map(pos-eps.xyy).t,
                            map(pos+eps.yxy).t - map(pos-eps.yxy).t,
                            map(pos+eps.yyx).t - map(pos-eps.yyx).t ) );
}

float ear(vec3 p)
{
    float res = 1.0;
    
    p = rotate(p,vec3(0.0,0.0,1.0),radians(-95.0));
    p.x += 0.1*cos(radians(p.y*240.0));
    p.y /= 1.6;
    p.xz /= 0.8;
    float d = sdCone(p, vec3(radians(30.0),0.2,0.3));
    float s = sdSphere(p+vec3(0.0,0.3,0.0),0.2);
    res = opMorph(d,s,0.8);
    
    return res;
}

float body(vec3 p)
{
    float res = 1.0;
    
    float b = udRoundBox(p,vec3(0.3,0.4,0.05),0.05);
    float s = sdSphere(p, 0.5);
    res = opMorph(b,s,0.6);
    
    return res;
}

float leg(vec3 p)
{
    float res = 1.0;
    
    vec3 cp = p;
    cp.z -= 1.0*cp.y*cp.y;
    float c = sdCylinder(cp, vec2(0.025,0.25)) - 0.01;
    c += cp.y*cp.y;
    
    vec3 sp = p+vec3(0.0,0.25,0.0);
    sp.z *= 0.8;
    float s = sdSphere(sp, 0.15);
    s /= 1.6;
    
    sp += vec3(0.0,0.1,0.0);
    float b = sdBox(sp, vec3(0.5,0.1,0.5));
    s = opS(s,b);
    
    res = opU(c,s);
    
    return res;
}

float arm(vec3 p)
{
    float res = 1.0;
    
    float finger_width = 0.0055;
    
    vec3 arm_point[3];
    arm_point[0] = vec3(0.0,0.0,0.0);
    arm_point[1] = vec3(-0.2,-0.05,-0.1);
    arm_point[2] = vec3(-0.1,-0.2,-0.3);
    
    vec3 finger1_point[2];
    finger1_point[0] = vec3(0.0000, 0.000, 0.0050);
    //finger1_point[1] = vec3(0.0575,-0.015, 0.0000);
    finger1_point[1] = vec3(0.0550,-0.030,-0.0375);
    
    vec3 finger2_point[2];
    finger2_point[0] = vec3(0.010, 0.0000, 0.0000);
    //finger2_point[1] = vec3(0.040, 0.0125,-0.0375);
    finger2_point[1] = vec3(0.045,-0.0250,-0.0750);
    
    vec3 finger3_point[2];
    finger3_point[0] = vec3(-0.0100, 0.0000, 0.0000);
    //finger3_point[1] = vec3( 0.0175, 0.0125,-0.0375);
    finger3_point[1] = vec3( 0.0225,-0.0250,-0.0750);
    
    vec3 finger4_point[2];
    finger4_point[0] = vec3(-0.0250,  0.0000, 0.0000);
    //finger4_point[1] = vec3(-0.0125,  0.0125,-0.0375);
    finger4_point[1] = vec3( 0.00025,-0.0250,-0.0750);
    
    float a = sdBezier(arm_point[0],
                       arm_point[1],
                       arm_point[2],
                       p,0.025).x;
    
    float h1 = 
        sdSegment(
        //sdBezier(
            finger1_point[0],
            finger1_point[1],
        //  finger1_point[2],
            p-arm_point[2]).x - finger_width;
    res = smin(a,h1,0.01);
    
    float h2 = 
        sdSegment(
        //sdBezier(
            finger2_point[0],
            finger2_point[1],
        //  finger2_point[2],
            p-arm_point[2]).x - finger_width;
    res = smin(res,h2,0.0075);
    
    float h3 = 
        sdSegment(
        //sdBezier(
            finger3_point[0],
            finger3_point[1],
        //  finger3_point[2],
            p-arm_point[2]).x - finger_width;
    res = smin(res,h3,0.0075);
    
    float h4 = 
        sdSegment(
        //sdBezier(
            finger4_point[0],
            finger4_point[1],
        //  finger4_point[2],
            p-arm_point[2]).x - finger_width;
    res = smin(res,h4,0.0075);
    
    return res;
}

float field1(vec3 p)
{
    float res = 1.0;
    float scale = 0.4;
    float k = 0.02;
    
    p += vec3(0.0,-0.4,0.0);
    
    vec3 p_ear1 = (p+vec3(-0.55,-0.3,0.0)) / scale;
    vec3 p_ear2 = (p+vec3(0.55,-0.3,0.0)) / scale;
    p_ear2.x = -p_ear2.x;
    res = opU(ear(p_ear1)*scale,
              ear(p_ear2)*scale);
    vec3 p_body = p + vec3(0.0,0.05,0.0);
    res = smin(res,body(p_body),k);
    
    vec3 p_leg1 = rotate(p+vec3(0.25,0.6,0.05),vec3(0.0,1.0,0.0),radians(10.0));
    res = opU(res,leg(p_leg1));
    vec3 p_leg2 = rotate(p+vec3(-0.25,0.6,0.05),vec3(0.0,1.0,0.0),radians(-10.0));
    res = opU(res,leg(p_leg2));
    
    vec3 p_arm1 = p + vec3(0.4,0.0,0.0);
    res = smin(res,arm(p_arm1),k);
    vec3 p_arm2 = p + vec3(-0.4,0.0,0.0);
    p_arm2.x = -p_arm2.x;
    res = smin(res,arm(p_arm2),k);
    
    return res;
}


float eye(vec3 p)
{
    float res = 1.0;

    res = sdSphere(p, 0.2);

    return res;
}
float field2(vec3 p)
{
    float res = 1.0;

    res = eye(p);

    return res;
}

Intersection map( in vec3 p )
{

    Intersection res,i;
    float id = 0.0;

    i = Intersection( sdPlane(p,vec3(0.0,1.0,0.0),1.0), id+1.0);
    //i = Intersection( sdPlane(ip, vec3(0.0,1.0,0.0), 0.1), id);
    res = i;
    p = rotate(p,vec3(0.0,1.0,0.0),radians(time*5.0));
    i = Intersection(field1(p), id);
    res = opU(res,i);
    i = Intersection(field1(p), id+1.5);
    res = opU(res,i);
        
    return res;
}

vec2 tr(vec2 p)
{
    p = -1.0+2.0*p/resolution.xy;
    p.x *= resolution.x/resolution.y;
    return p;
}

vec3 lig = vec3(-1.0,1.0,0.25);
vec3 po =  vec3(0.0,4.0,-2.25);
vec3 ta =  vec3(0.0,0.0,0.0);

void main()
{
    vec2 tch = tr(touch);

    //po = rotate(po,vec3(1.0,0.0,0.0),radians(40.0*tch.y));
    po = rotate(po,vec3(0.0,1.0,0.0),radians(90.0*tch.x));
    po += (ta-po)*tch.y;
    
    vec3 ro,rd;
    generateRay(ro,rd,po,ta,gl_FragCoord.xy);
    ro *= 0.5;
    vec3 col = vec3(0.0);

    Intersection is = intersect(ro,rd);
    
    vec3 arr1[COLORS];
    arr1[0] = vec3(0.0,0.4,0.0);
    arr1[1] = vec3(0.9,0.6,0.0);
    arr1[2] = vec3(0.2,0.6,0.8);
    arr1[3] = vec3(0.9,0.9,0.0);
    arr1[4] = vec3(0.3,0.6,0.3);
    arr1[5] = vec3(0.0,0.1,0.7);
    arr1[6] = vec3(0.9,0.1,0.1);
    
    vec3 arr2[COLORS];
    arr2[0] = vec3(0.0,0.3,0.0);
    arr2[1] = vec3(0.5,0.6,0.0);
    arr2[2] = vec3(0.5,0.6,0.7);
    arr2[3] = vec3(0.8,0.0,0.2);
    arr2[4] = vec3(0.5,0.6,0.7);
    arr2[5] = vec3(0.5,0.6,0.0);
    arr2[6] = vec3(0.1,0.6,0.2);
    
    
    if( is.t>0.0 )
    {
        // trick to use dynamic indexing
        for(int id = 0; id < COLORS; id++)
        {
            if(id != floor(mod(is.id,float(COLORS))))
                continue;
            vec3 pos = ro + is.t*rd;
            vec3 nor = calcNormal(pos);
            #ifdef POINT_LIGHT
            vec3 to_light = normalize(lig-pos);
            #else
            vec3 to_light = normalize(lig);
            #endif
            float sha = calcSoftshadow( pos + nor*0.001, to_light, 16.0 );
            float occ = calcOcclusion( pos, nor );
            col =  0.05*arr1[id] + 0.95*arr1[id]*clamp( dot( nor, to_light ), 0.0, 1.0 ) * sha;
            col += arr2[id]*clamp( nor.y, 0.0, 1.0 )*occ;
            col *= exp( -0.1*is.t );
            break;
        }
    }

    col = pow( clamp(col,0.0,1.0), vec3(0.45) );
       
    gl_FragColor = vec4( col, 1.0 );
}

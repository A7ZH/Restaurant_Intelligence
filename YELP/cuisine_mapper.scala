import scala.io.Source
import scala.collection.immutable.HashMap
import java.io.{BufferedWriter, FileWriter}

val cuisineMap = 
Source.fromFile("YELP-Crawl-Run-2019-12-28T103701Z.csv", "ISO-8859-1").getLines.drop(1)
      .flatMap(rawTxtLine=>{
         val lineSplitArr = rawTxtLine.split(",(?=\\S)");
         val name = lineSplitArr(0).stripPrefix("\"").stripSuffix("\"");
         val addr = lineSplitArr(1).stripPrefix("\"").stripSuffix("\"");
         val cuisine_tags = lineSplitArr(2).stripPrefix("\"").stripSuffix("\"").split(';').map(_.trim);
         cuisine_tags.map(t=>(t,(name, addr)))
       })
      .foldLeft(HashMap[String, List[Tuple2[String,String]]]())(
         (cuisineMapSoFar, nextEntry)=>{
           val cuisine = nextEntry._1;
           val nameAddr = nextEntry._2;
           if(cuisineMapSoFar.contains(cuisine)) 
                cuisineMapSoFar + (cuisine -> (cuisineMapSoFar(cuisine) :+ nameAddr)) 
           else cuisineMapSoFar + (cuisine -> List[(String,String)]((nameAddr)))
         })


//val file = "cuisine_map_neat.txt"
val file = "cuisine_map.txt"
val writer = new BufferedWriter(new FileWriter(file))
for(c<-cuisineMap.toList.sortWith((t1,t2)=>t1._1<t2._1)){
  val len = c._2.size
  val cuisine = c._1
  writer.write(raw"""$cuisine [$len]: """)
  var i=1
  for(r<-c._2){
    if(i==len) writer.write(r.toString) else writer.write(r.toString+", ")
    i+=1
  }
  writer.write("\n")
//writer.write("\n=================================================================\n")
}
writer.close()
